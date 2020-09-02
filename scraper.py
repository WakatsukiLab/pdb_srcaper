import os
import time
import datetime
import json
import argparse
import requests
from urllib.parse import quote


def scrape(url):
    r = requests.get(url)
    html = r.content.decode("utf-8")
    return html


def download(url, dest):
    r = requests.get(url)
    open(dest, "wb").write(r.content)


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("keyword", type=str, help="Keyword for PDB website search")
    p.add_argument("--n_results", "-n", type=int, default=5, help="Maxmium number of results to be scraped")
    p.add_argument("--dest_path", type=str, default="PDBs", help="Path where PDB files will be saved")
    p.add_argument("--verbose", "-v", action="store_true", help="Be verbose")
    return p.parse_args()


def main():
    args = parse_args()
    json_text = '{"query":{"parameters":{"value":"plpro"},"service":"text","type":"terminal","node_id":0},"return_type":"entry","request_options":{"pager":{"start":0,"rows":100},"scoring_strategy":"combined","sort":[{"sort_by":"rcsb_accession_info.initial_release_date","direction":"desc"}]}}'
    params = json.loads(json_text)
    params["query"]["parameters"]["value"] = args.keyword
    # print(json.dumps(params))
    url = "https://search.rcsb.org/rcsbsearch/v1/query?json=" + quote(json.dumps(params))
    print("Fetching {}".format(url))
    html = scrape(url)
    results = json.loads(html)
    pdb_list = [result["identifier"] for result in results["result_set"]]
    print("Found the following:" + pdb_list.__repr__())
    n = min(args.n_results, len(pdb_list))
    os.makedirs(args.dest_path, exist_ok=True)
    for pdb_id in pdb_list[:n]:
        dest = "{}/{}.pdb".format(args.dest_path, pdb_id)
        if os.path.isfile(dest):
            print("{} exists, skipping...".format(pdb_id))
            continue
        url = "https://files.rcsb.org/download/{}.pdb".format(pdb_id)
        print("Fetching {}".format(url))
        download(url, dest)


if __name__ == "__main__":
    main()
