#  Copyright (C) 2018 Minori Hiraoka
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see https://www.gnu.org/licenses/gpl.txt.

import json
import sys
import getopt
import requests
import datetime
import html


def main(argv):
    hbl = ''
    year = ''

    try:
        if len(argv) == 0:
            raise getopt.GetoptError
        opts, args = getopt.gnu_getopt(argv, "hb:y:", ["help", "hbl=", "year="])
    except getopt.GetoptError:
        print("Usage: customs.py -b <H B/L> -y <year - optional>\n"
              "\n"
              "-b, --hbl: H B/L\n"
              "-y, --year: Year (optional), defaults to this year\n"
              "-h, --help: Shows help\n")
        sys.exit(1)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("Usage: customs.py -b <H B/L> -y <year - optional>\n"
                  "\n"
                  "-b, --hbl: H B/L\n"
                  "-y, --year: Year (optional), defaults to this year\n"
                  "-h, --help: Shows help\n")
            sys.exit()
        elif opt in ("-b", "--hbl"):
            hbl = arg
        elif opt in ("-y", "--year"):
            year = arg

    if year == "":
        year = str(datetime.datetime.now().year)

    summary_json = get_summary_info(hbl, year)
    summary_decoded = json.loads(summary_json)

    # TODO: Dynamically search from dict without hard coding the path
    cargo_management_number = summary_decoded['resultList'][0]['cargMtNo']

    detail_json = get_detailed_info(cargo_management_number)
    detail_decoded = json.loads(detail_json)

    display_info(detail_decoded)


def get_summary_info(hbl, year):
    url = "https://unipass.customs.go.kr/csp/myc/bsopspptinfo/cscllgstinfo/ImpCargPrgsInfoMtCtr" \
          "/retrieveImpCargPrgsInfoLst.do"
    payload = {"firstIndex": "0",
               "page": "1",
               "pageIndex": "1",
               "pageSize": "10",
               "pageUnit": "10",
               "recordCountPerPage": "10",
               "qryTp": "2",
               "cargMtNo": "",
               "mblNo": "",
               "hblNo": hbl,
               "blYy": year}

    result = requests.post(url, data=payload)

    return html.unescape(result.text)


def get_detailed_info(cargo_management_number):
    url = "https://unipass.customs.go.kr/csp/myc/bsopspptinfo/cscllgstinfo/ImpCargPrgsInfoMtCtr" \
          "/retrieveImpCargPrgsInfoDtl.do"
    payload = {"firstIndex": "0",
               "recordCountPerPage": "10",
               "page": "1",
               "pageIndex": "1",
               "pageSize": "10",
               "pageUnit": "10",
               "cargMtNo": cargo_management_number}

    result = requests.post(url, data=payload)

    return html.unescape(result.text)


def display_info(detail_decoded):
    mbl = detail_decoded["resultListM"]["mblNo"]
    hbl = detail_decoded["resultListM"]["hblNo"]
    cargo_management_number = detail_decoded["resultListM"]["cargMtNo"]

    cargo_liner = detail_decoded["resultListM"]["shcoFlcoSgn"]
    cargo_liner_number = detail_decoded["resultListM"]["sanm"]
    cargo_load_port = detail_decoded["resultListM"]["loadPortAirptCd"]
    cargo_unload_port = detail_decoded["resultListM"]["unldPortAirptCd"]
    cargo_custom_name = detail_decoded["resultListM"]["etprCstmSgn"]
    cargo_name = detail_decoded["resultListM"]["prnm"]
    cargo_type = detail_decoded["resultListM"]["blPcd"] + " (" + detail_decoded["resultListM"]["blPcdNm"] + ")"
    cargo_count = detail_decoded["resultListM"]["cmdtGcnt"] + " " + detail_decoded["resultListM"]["pckKcd"]
    cargo_weight = detail_decoded["resultListM"]["cmdtWght"] + " " + detail_decoded["resultListM"]["kg"]
    cargo_unload_date = detail_decoded["resultListM"]["etprDt"]

    # TODO: Difference between prgsSttsEn and cargTpcdEn?
    current_status = detail_decoded["resultListM"]["prgsSttsEn"] + \
                     " (" + detail_decoded["resultListM"]["prgsStts"] + ")"

    print("M B/L - H B/L:", mbl, "-", hbl)
    print("Cargo management number:", cargo_management_number)

    print("")

    print("Cargo Liner:", cargo_liner, cargo_liner_number)
    print("Cargo unload date:", cargo_unload_date)
    print("Cargo from:", cargo_load_port, "to", cargo_unload_port)
    print("Cargo goes through", cargo_custom_name)
    print("Cargo name:", cargo_name)
    print("Cargo type:", cargo_type)
    print("Cargo count:", cargo_count)
    print("Cargo weight:", cargo_weight)

    print("")

    print("Current status:", current_status)

    print("")

    print("Details\n--------")

    for idx, item in enumerate(reversed(detail_decoded["resultListL"])):
        print("Index:", idx+1)
        print("Date:", item["prcsDttm"])
        print("Progress:", item["cargTrcnRelaBsopTpcd"])

        if item["snarAddr"] != "" and item["snarTelno"] != "":
            print("Current location:", item["snarAddr"], "/", item["snarTelno"])

        print("--------")


if __name__ == "__main__":
    main(sys.argv[1:])
