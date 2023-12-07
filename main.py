from CTT_metrics import RISEvaluation, SPLOTcreateTable

print("This replication package allows to reproduce results from Section 7.")
answer = None
while answer not in ["1", "2"]:
    print("Please type \"1\" to begin reproduction of results for Section 7.1, type \"2\" for those of Section 7.2.")
    answer = input()

if answer == "1":
    print("Section 7.1 aims at evaluating the impact of our three improvements on performance.")
    print("To reproduce Table 4, some test suites have been stored. You can also choose to re-generate all test suites to reproduce results (takes longer !).")
    recompute = False
    while answer not in ["recompute", "storage"]:
        print("Please type \"recompute\" to regenerate all test suites (takes longer), type \"storage\" to use existing test suites.")
        answer = input()
    if recompute == "recompute":
        recompute = True
    print("Starting reproduction of Table 4. It might take several minutes or up to an hour on a slow machine if you chose to recompute test suites.")
    RISEvaluation(1000, ["0", "1", "2", "3", "1&2", "2&3", "1&3", "1&2&3"], recompute, plot=None)

else:
    print("Section 7.2 uses SPLOT to evaluate how CTT fares in comparison to CIT.")
    print("Reproduction of Table 5 is very time-consuming (several hours, if everything is recompute up to days). To allow fast reproduction, we propose several parameters.")
    print("First, you can choose an upper limit on the size of feature models for reproduction. Options are: 20, 30, 40, 50, 70, 100")
    print("We advise 50 for fast reproduction.")
    limit = 100
    options = ["20", "30", "40", "50", "70", "100"]
    while answer not in options:
        print("Please an upper limit on size for feature models among : " + str(options))
        answer = input()
    limit = int(answer)
    print("For faster reproduction, test suites have been stored in advance. You can also choose to re-generate all test suites to reproduce results (takes A LOT longer; it uses multi-threading for faster computations).")
    recompute = False
    while answer not in ["recompute", "storage"]:
        print("Please type \"recompute\" to regenerate all test suites (takes longer), type \"storage\" to use existing test suites.")
        answer = input()
    if answer == "recompute":
        recompute = True

    print("Starting reproduction of Table 5. It might take minutes or dozens of hours on a slow machine if you chose to recompute test suites and high limit for size of feature models.")
    categories = [cat for cat in [[10, 20], [20, 30], [30, 40], [40, 50], [50, 70], [70, 100]] if cat[1] <= limit]
    SPLOTcreateTable(categories, recompute=recompute)
