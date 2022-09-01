from matplotlib import pyplot as plt
import pandas as pd
from collections import defaultdict
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix
from sklearn.metrics import f1_score
import numpy as np
import os
import math
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
import argparse

def get_clf_eval(y_test, pred, avg='micro'):
    confusion = confusion_matrix(y_test, pred)
    accuracy = accuracy_score(y_test, pred)
    precision = precision_score(y_test, pred, average=avg)
    recall = recall_score(y_test, pred, average=avg)
    f1 = f1_score(y_test, pred, average=avg)
    print('Confusion Matrix')
    print(confusion)
    print('Accuracy:{}, Precision:{}, Recall:{}, F1:{}'.format(accuracy, precision, recall, f1))
    
    return confusion, accuracy, precision, recall, f1

def get_according_to_label(y_test, pred):
    confusion = confusion_matrix(y_test, pred)
    rec_bar = []
    for i in range(confusion.shape[0]):
        row_sum = np.sum(confusion[i])
        ans = confusion[i,i]
        if row_sum == 0:
            rec_bar.append(0)
        else:
            rec_bar.append(ans / row_sum)
    recall_0 = rec_bar[0]
    recall_1 = rec_bar[1]
    recall_2 = rec_bar[2]
    
    prec_bar = []
    for i in range(confusion.shape[0]):
        col_sum = np.sum(confusion[:,i])
        ans = confusion[i,i]
        if col_sum == 0:
            prec_bar.append(0)
        else:
            prec_bar.append(ans / col_sum)
    precision_0  = prec_bar[0]
    precision_1 = prec_bar[1]
    precision_2 = prec_bar[2]
    
    return recall_0, precision_0, recall_1, precision_1, recall_2, precision_2

def update_result(propertyname, result_dict, property2eval):
    for k,v in result_dict.items():
        property2eval[propertyname][k] = v
    return property2eval

def get_exponent(a):
    # ret1 <= a < ret2
    base = 1
    while base <= a:
        base *= 2
    while base > a:
        base /= 2
    ret1 = base
    
    base = ret1
    while base <= a:
        base *= 2
    ret2 = base
    
    return math.log2(ret1), math.log2(ret2)

def split_data(args, data):
    ## Split
    need_split_flag = False
    if args.repeat_idx > 0:
        input_test_name = "../dataset/{}/test_hindex_{}_{}.txt".format(args.input_dir, args.k, args.repeat_idx)
        input_valid_name = "../dataset/{}/valid_hindex_{}_{}.txt".format(args.input_dir, args.k, args.repeat_idx)
    else:
        input_test_name = "../dataset/{}/test_hindex_{}.txt".format(args.input_dir, args.k)
        input_valid_name = "../dataset/{}/valid_hindex_{}.txt".format(args.input_dir, args.k)
    if os.path.isfile(input_test_name) is False:
        need_split_flag = True
    if os.path.isfile(input_valid_name) is False:
        need_split_flag = True
    if need_split_flag:
        hedgename_list = data['hedgename'].unique()
        numhedges = list(range(len(hedgename_list)))
        # train_hindex, test_hindex = train_test_split(numhedges, test_size = 0.2, random_state = 21)
        _train_hindex, test_hindex = train_test_split(numhedges, test_size=0.2, random_state=21)
        train_hindex, valid_hindex = train_test_split(_train_hindex, test_size=0.25, random_state=21)

        train_hedgename = hedgename_list[train_hindex]
        valid_hedgename = hedgename_list[valid_hindex]
        test_hedgename = hedgename_list[test_hindex]

        train_index = []
        valid_index = []
        test_index = []
        for hedgename in train_hedgename:
            train_index += data.index[data['hedgename'] == hedgename].tolist()
        for hedgename in valid_hedgename:
            valid_index += data.index[data['hedgename'] == hedgename].tolist()
        for hedgename in test_hedgename:
            test_index += data.index[data['hedgename'] == hedgename].tolist()
        assert len(valid_index) > 0
        assert len(test_index) > 0
        with open(input_valid_name, "w") as f:
            for hedgename in valid_hedgename:
                f.write(str(hedgename) + "\n")
        with open(input_test_name, "w") as f:
            for hedgename in test_hedgename:
                f.write(str(hedgename) + "\n")
    else:
        valid_hedgename = []
        with open(input_valid_name, "r") as f:
            for line in f.readlines():
                if args.exist_hedgename:
                    valid_hedgename.append(line.rstrip())
                else:
                    valid_hedgename.append(int(line.rstrip()))
        test_hedgename = []
        with open(input_test_name, "r") as f:
            for line in f.readlines():
                if args.exist_hedgename:
                    test_hedgename.append(line.rstrip())
                else:
                    test_hedgename.append(int(line.rstrip()))
        valid_index = []
        test_index = []
        for hedgename in valid_hedgename:
            valid_index += data.index[data['hedgename'] == hedgename].tolist()
        for hedgename in test_hedgename:
            test_index += data.index[data['hedgename'] == hedgename].tolist()
        train_index = list(set(range(len(data))) - set(test_index) - set(valid_index))
        assert len(test_index) > 0 or len(valid_index) > 0

    assert len(set(train_index).intersection(set(test_index))) == 0
    assert len(set(train_index).intersection(set(valid_index))) == 0
    assert len(set(test_index).intersection(set(valid_index))) == 0
    
    return train_index, valid_index, test_index

def get_result(args, Y_test, pred, dirname, name):
    confusion, accuracy, precision_micro, recall_micro, f1_micro = get_clf_eval(Y_test, pred, avg='micro')
    confusion, accuracy, precision_macro, recall_macro, f1_macro = get_clf_eval(Y_test, pred, avg='macro')
    recall_0, precision_0, recall_1, precision_1, recall_2, precision_2 = get_according_to_label(Y_test, pred)
    result_dict = { "accuracy" : accuracy,
               "precision_micro" : precision_micro,
               "precision_macro" : precision_macro,
               "recall_micro" : recall_micro,
               "recall_macro" : recall_macro,
               "f1_micro" : f1_micro,
               "f1_macro" : f1_macro,
               "recall_0" : recall_0,
               "precision_0" : precision_0,
               "recall_1" : recall_1,
               "precision_1" : precision_1,
               "recall_2" : recall_2,
               "precision_2" : precision_2
    }
    if args.repeat_idx > 0:
        base_output = dirname + args.prefix + "{}_confusion_{}.txt".format(name, args.repeat_idx)
    else:
        base_output = dirname + args.prefix + "{}_confusion.txt".format(name)
    with open(base_output, "w") as f:
        for r in range(3):
            for c in range(3):
                f.write(str(confusion[r][c]))
                if c == 2:
                    f.write("\n")
                else:
                    f.write("\t")
    return result_dict

# Main --------------------------------------------------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='Argparse Tutorial')
parser.add_argument('--input_dir', default='DBLP2', type=str)
parser.add_argument('--exist_hedgename', action='store_true')
parser.add_argument('--k', default=10000, type=int)
parser.add_argument('--input_name', default='whole_data', type=str)
parser.add_argument('--repeat_idx', default=0, type=int)
parser.add_argument('--prefix', default='', type=str, help="onehot_ / '' nothing")
args = parser.parse_args()

property2eval = defaultdict(dict) # "all" or "degree" ... -> "acc" or "precision_micro" ... -> "model name" 
baseline2eval = defaultdict(dict) # baseline_0 or baseline_1  -> "acc" or "precision_micro" ...

identity = ['node reindex']
nongiven_features = ['degree', 'eigenvec', 'kcore', 'pagerank']
vrank_features = ['degree_vrank', 'eigenvec_vrank', 'kcore_vrank', 'pagerank_vrank']
erank_features = ['degree_erank', 'eigenvec_erank', 'kcore_erank', 'pagerank_erank']
all_cols = nongiven_features + vrank_features + erank_features # identity +  + hedge_features

# Read Data
if args.repeat_idx > 0:
    inputname = "../dataset/{}/{}_{}_{}.txt".format(args.input_dir, args.input_name, args.k, args.repeat_idx)
else:
    inputname = "../dataset/{}/{}_{}.txt".format(args.input_dir, args.input_name, args.k)
usecols = ['pos', 'hedgename'] + all_cols
data = pd.read_csv(inputname, usecols=usecols)
### post process: onehot
if args.prefix == "onehot_":
    for value_col in nongiven_features:
        min_v = min(data[value_col])
        max_v = max(data[value_col])
        base, _ = get_exponent(min_v)
        keys = []
        for i, row in data.iterrows():
            ret1, ret2 = get_exponent(row[value_col])
            key = ret1 - base
            keys.append(key)
        data[value_col] = keys
    
# Split
train_index, valid_index, test_index = split_data(args, data)
column_indexes = [idx for (idx,col) in enumerate(data.columns) if col != 'hedgename' and col != 'pos']
X_train = data.iloc[train_index, column_indexes].values
X_valid = data.iloc[valid_index, column_indexes].values
Y_train = data.iloc[train_index, -1].values
Y_valid = data.iloc[valid_index, -1].values
print("Valid Len", len(Y_valid))

# Baseline
basedirname = "../nongraph_results/" + args.input_dir + "_" + str(args.k) + "/"
if os.path.isdir(basedirname) is False:
    os.makedirs(basedirname)
### Baseline 0
baseline0_pred = [np.random.randint(3) for _ in range(len(Y_valid))]
baseline0_result = get_result(args, Y_valid, baseline0_pred, basedirname, "baseline0")
for evalname in baseline0_result:
    baseline2eval["baseline0"][evalname] = baseline0_result[evalname]
### Baselin 1
if args.input_dir == "DBLP2":
    baseline1_pred = [1 for _ in range(len(Y_valid))]
elif args.input_dir == "emailEnron":
    baseline1_pred = [0 for _ in range(len(Y_valid))]
baseline1_result = get_result(args, Y_valid, baseline1_pred, basedirname, "baseline1")
for evalname in baseline1_result:
    baseline2eval["baseline1"][evalname] = baseline1_result[evalname]
for baselinename in baseline2eval.keys():
    if args.repeat_idx > 0:
        base_output = basedirname + baselinename + "_{}.txt".format(args.repeat_idx)
    else:
        base_output = basedirname + baselinename + ".txt"
    with open(base_output, "w") as f:
        for evalname in baseline2eval[baselinename]:
            f.write(evalname + "\t" + str(baseline2eval[baselinename][evalname]) + "\n")

# Save Directory
dirname = "../nongraph_results/" + args.input_dir + "_" + str(args.k) + "/RandomForest/"
if os.path.isdir(dirname) is False:
    os.makedirs(dirname)
figdirname = "../figures/" + args.input_dir + "_" + str(args.k) + "/RandomForest/"
if os.path.isdir(figdirname) is False:
    os.makedirs(figdirname)

# Target column list
search = {"All" : all_cols,
         "vfeat" : nongiven_features,
         "vrank" : vrank_features,
         "erank" : erank_features,
         "vfeat_vrank": nongiven_features + vrank_features,
         "vfeat_erank": nongiven_features + erank_features,
         "vrank_erank": vrank_features + erank_features}
for vrank_name in vrank_features:
    search[vrank_name] = nongiven_features + [vrank_name]

# Run
for name, col in search.items():
    usecols = col + ['pos']
    d = data[usecols]
    
    # Split
    X_train = d.iloc[train_index, :-1].values
    X_valid = d.iloc[valid_index, :-1].values
    Y_train = d.iloc[train_index, -1].values
    Y_valid = d.iloc[valid_index, -1].values
    
    # Scaling
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_valid = scaler.transform(X_valid)
    
    # Random Forest
    rf = RandomForestClassifier(n_estimators = 10, criterion = 'entropy', random_state = 42)
    rf.fit(X_train, Y_train)
    Y_pred = rf.predict(X_valid)
    result_dict = get_result(args, Y_valid, Y_pred, dirname, name)
    if args.repeat_idx > 0:
        feat_output = figdirname + args.prefix + "feature_ranking_{}_{}.txt".format(name, args.repeat_idx)
        featfig = figdirname + args.prefix + "feature_ranking_{}_{}.jpg".format(name, args.repeat_idx)
    else:
        feat_output = figdirname + args.prefix + "feature_ranking_{}.txt".format(name)
        featfig = figdirname + args.prefix + "feature_ranking_{}.jpg".format(name)
    property2eval = update_result(name, result_dict, property2eval)
    # feature importance
    importances = rf.feature_importances_
    std = np.std([tree.feature_importances_ for tree in rf.estimators_], axis=0)
    indices = np.argsort(importances)[::-1]
    with open(feat_output, "w") as f:
        for fidx in range(X_train.shape[1]):
            f.write("{}. feature {} ({:.3f})".format(fidx + 1, d.columns[indices][fidx], importances[indices][fidx]))
    # feature ranking figure
    plt.figure(dpi=100, figsize=(7,7))
    plt.title("Feature Importances")
    plt.bar(range(X_train.shape[1]), importances[indices], color="r", yerr=std[indices], align='center')
    plt.xticks(range(X_train.shape[1]), d.columns[indices], rotation=90)
    plt.xlim([-1, X_train.shape[1]])
    plt.savefig(featfig, bbox_inches='tight')
    plt.close()

# Save Results
xs = list(property2eval["All"].keys())
for prop in property2eval.keys():
    if args.repeat_idx > 0:
        outputname = dirname + args.prefix + prop + "_{}.txt".format(args.repeat_idx)
    else:
        outputname = dirname + args.prefix + prop + ".txt"
    with open(outputname, "w") as f:
        for x in xs:
            f.write(x + "\t" + str(property2eval[prop][x]) + "\n")
            