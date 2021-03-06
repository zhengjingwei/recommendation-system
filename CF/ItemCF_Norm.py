from utils import *

def item_similarity(train):
    """ 
    """ 
    N = dict() # item popularity
    C = dict() 
    for user,items in train.items():
        for i in items:
            N.setdefault(i,0)
            N[i] += 1
            C.setdefault(i,dict())
            for j in items:
                if i == j:
                    continue
                C[i].setdefault(j,0)
                C[i][j] += 1 / math.log(1 + len(items)) # IUF
    
    W = C.copy()
    Wi_max =  dict()
    for i, related_items in C.items():
        for j, c_ij in related_items.items():
            W[i][j] = c_ij / math.sqrt(N[i] * N[j]) # penalty for hot items
            Wi_max.setdefault(i,0)
            if W[i][j] > Wi_max[i]:
                Wi_max[i] = W[i][j]
    
    # normalization for Wij
    for i, items in W.items():
        for j , wij in items.items():
            W[i][j] /= Wi_max[i]    

    return W


def recommend(users, train, W, K=3, N=10):
    """
    @param users:   history item list of the user 
    @param W:       item similarity matrix
    @param K:       num of considering similar items
    @param N:       max num of items for each user
    """
    ret = dict()
    for u in users:
        rank = get_recommendation(train[u], W, K)
        r = sorted(rank.items(), key = operator.itemgetter(1), \
                   reverse = True)
        if len(r) > N:
            ret[u] = r[:N]
        else:
            ret[u] = r

    return ret


def get_recommendation(items, W, K=3):

    rank = dict()
    for i, pi in items.items():
        for j, w_ij in sorted( W[i].items() ,key=operator.itemgetter(1), reverse = True)[0:K]:
            if j in items:      # filter existed items
                continue 
            rank.setdefault(j,0)
            rank[j] += pi * w_ij
            
    return rank  


if __name__ == '__main__':

    dataset = '../data/ml-100k/u.data'
    data = read_data(dataset)
    train_times = 8
    K = 3           
    N = 10          
    prec = 0
    rec = 0
    cover = 0
    popu = 0
    t1 = time.time()

    for i in range(train_times):

        rawTrain, rawTest = split_data(data, train_times, i, seed=0)
        train = data_transform(rawTrain)
        test = data_transform(rawTest)
        W = item_similarity(train)
        result = recommend(test.keys(), train, W, K, N)
        
        rec += recall(test, result, N)
        prec += precision(test, result, N)
        cover += coverage(train, result, N)
        popu += popularity(train, result)
    
    prec = prec / train_times
    rec  = rec / train_times
    cover = cover / train_times
    popu = popu / train_times
    print('precision = ',prec)
    print('recall = ',rec)
    print('coverage = ',cover)
    print('popularity = ', popu)
    print('time = {:.1f} s'.format(time.time() - t1))