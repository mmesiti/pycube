#!/usr/bin/env python3
##################################################################
# Author    : Dr Chennakesava Kadapa
# Date      : 02-Apr-2020
# Copyright : @SA2C
##################################################################
#
# Usage:
#
# barchartNfuncs.py <cubex-filename>  <metric>  <exclincl>  <nfuncs>
# <cubex-filename> : name of the .cubex file
# <metric>         : visits, time, max_time, min_time
# <exclincl>       : T = Exclusive, F = Inclusive
# <nfuncs>         : number of functions to plot
#
# Example:
#
# python3  barchartNfuncs.py  profile.cubex  time T  10
#
################################################################################
"""
Similar to barchartLevelwise.py, but processes multiple `.cubex` files.
"""
if __name__ == "__main__":
    import merger as mg
    import index_conversions as ic
    import pandas as pd
    import matplotlib.pyplot as plt
    import calltree as ct
    import sys
    import os
    import numpy as np

    data_dir = "../test_data"
    inpfilename = os.path.join(data_dir, "profile-25m-nproc40-nsteps10.cubex")
    metric = "time"
    exclincl = False
    nfuncs = 10

    def get_metric_by_level(inpfilename):
        """
        get depth level for each function in the call tree
        """
        print(f"Processing {inpfilename}")

        # This gives us a number of outputs
        # (see https://cupybelib.readthedocs.io/en/latest/merger.html)
        output_i = mg.process_cubex(inpfilename, exclusive=exclincl)

        parent_series = output_i.ctree_df.set_index("Cnode ID").loc[
            :, "Parent Cnode ID"
        ]

        # get depth level for each function in the call tree
        levels = ct.get_level(parent_series)

        # We convert the Cnode IDs to short callpaths in the dataframe.
        df_i = ic.convert_index(output_i.df, output_i.ctree_df, target="Short Callpath")

        # extract the data
        res = (
            df_i.reset_index()[["Short Callpath", "Thread ID", metric]]
            .groupby("Short Callpath")
            .sum()
            .sort_values([metric])[metric]
        )

        res_df = pd.DataFrame(res)

        time = res_df.reset_index()["time"]
        fname = res_df.reset_index()["Short Callpath"].str.extract(r"(\w+),([0-9]+)")[0]
        cnode_id = (
            res_df.reset_index()["Short Callpath"]
            .str.extract(r"(\w+),([0-9]+)")[1]
            .astype(int)
        )

        combined = pd.merge(
            left=(
                pd.concat([time, fname, cnode_id], axis="columns").rename(
                    {"time": "time", 0: "fname", 1: "Cnode ID"}, axis="columns"
                )
            ),
            right=levels.reset_index().rename({0: "level"}, axis="columns"),
            on="Cnode ID",
        )

        # to extract functions called only at the 3rd level
        time_data = combined[combined["level"] == 2].sort_values(
            by=["level", "time"], ascending=False
        )

        return time_data

    files = [
        "profile-5m-nproc40-nsteps10.cubex",
        "profile-10m-nproc40-nsteps10.cubex",
        "profile-25m-nproc40-nsteps10.cubex",
    ]

    time_data1, time_data2, time_data3 = [
        get_metric_by_level(os.path.join(data_dir, f)) for f in files
    ]

    X = np.arange(len(time_data1))

    plt.bar(X - 0.25, time_data1["time"], color="b", width=0.25, label="M1 mesh")
    plt.bar(X, time_data2["time"], color="r", width=0.25, label="M2 mesh")
    plt.bar(X + 0.25, time_data3["time"], color="g", width=0.25, label="M3 mesh")

    plt.xlabel("Function name", fontsize=14)
    plt.title(
        "metric="
        + metric
        + " "
        + ("(Exclusive)" if exclincl == True else "(Inclusive)"),
        fontsize=14,
    )
    plt.legend(frameon=False)

    metric_time_list = ["time", "max_time", "min_time"]

    if metric in metric_time_list:
        plt.ylabel("Time [s]", fontsize=14)
        plt.ylim(10 ** 1, 10 ** 5)
        plt.yscale("log")
    elif metric == "visits":
        plt.ylabel("Number of visits", fontsize=14)
    #    plt.yscale('log')
    #    if(max(data[:,2]) > 10**4):
    else:
        print("Metric type not supported!")
        sys.exit()

    plt.xticks(X, time_data1["fname"])
    plt.xticks(rotation=70)
    plt.tight_layout()
    plt.show()
