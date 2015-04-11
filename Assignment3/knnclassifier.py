__author__ = 'santhosh'

import numpy
import matplotlib.pyplot as plt
import os


def plotErrorForK(ks, errors, train_errors, test_errors):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    plt.title('Error Plot')
    plt.xlabel('K')
    plt.ylabel('Error')
    ax.plot(ks, errors, label='CrossValidation Error', color='r')
    ax.plot(ks, train_errors, label='Train Error', color='b')
    ax.plot(ks, test_errors, label='Test Error', color='g')
    imgFile = os.path.join(os.getcwd(), "Error plot")+'.png'
    print "Error plot logged to "+imgFile
    plt.savefig(imgFile,\
                 bbox_inches="tight")
    plt.close()

class KNNClassifier(object):
    def __init__(self, possible_k_values, cross_validation_fold):
        self.train_data = []
        self.train_sample_pair_wise_distance_matrix = {}
        self.train_result = []
        self.nFold = cross_validation_fold
        self.possible_k_values = possible_k_values
        self.k = -1

    def cosine_distance(self,x,y):
        denom = numpy.sqrt(numpy.dot(x,x)*numpy.dot(y,y))
        distance = 1 -(numpy.dot(x,y)/denom)
        return distance
    
    def calculatePairWiseDistanceForTrainSamples(self):
        n_samples, n_features = self.train_data.shape
        for i in range(n_samples):
            neighbor_distances = {j:self.cosine_distance(self.train_data[i], self.train_data[j])\
                                  for j in range(n_samples) if i != j}
            neighbor_distances = sorted(list(neighbor_distances.keys()), key = lambda key : neighbor_distances[key])
            self.train_sample_pair_wise_distance_matrix[i] = neighbor_distances
        
    def findKNearestNeigbors(self, x, k = None):
        if k == None:
            k = self.k
        n_samples, n_features = self.train_data.shape
        neighbor_distances_dict = dict()
        for i in range(n_samples):
            train_vector = self.train_data[i]
            distance_for_this_sample = self.cosine_distance(train_vector, x)
            neighbor_distances_dict[i] = distance_for_this_sample
        neighbors_array = sorted(list(neighbor_distances_dict.keys()), key = lambda key: neighbor_distances_dict[key])
        return neighbors_array[:k]

    def doNFoldCrossValidationAndMeasureK(self):
        n_samples, n_features = self.train_data.shape
        partition_size = n_samples/self.nFold
        test_idx_for_each_iter = []
        for i in range(0, n_samples, partition_size):
            test_idx_for_each_iter.append((i,i+partition_size))
        cross_validation_error_for_each_k = dict()
        for k in self.possible_k_values:
            error = 0
            for i in range(len(test_idx_for_each_iter)):
                start, end = test_idx_for_each_iter[i]
                train_data_for_iter, train_result_for_iter = [],[]
                for sample_idx in range(n_samples):
                    if sample_idx < start or sample_idx >= end:
                        train_data_for_iter.append(self.train_data[sample_idx])
                        train_result_for_iter.append(self.train_result[sample_idx])
                for test_idx in range(start,end):
                    knn = [neighbor for neighbor in self.train_sample_pair_wise_distance_matrix[test_idx] if neighbor < start or neighbor >= end][:k]
                    label = self.getMajorityClassLabelsForKNN(knn, train_data_for_iter, train_result_for_iter)
                    test_label = self.train_result[test_idx]
                    if label != test_label:
                        error += 1
            cross_validation_error_for_each_k[k] = error/n_samples
        self.k = min(cross_validation_error_for_each_k.keys(), key = lambda key: cross_validation_error_for_each_k[key])
        print 'Minimum error with k: ', self.k
        return cross_validation_error_for_each_k.values()

    def getMajorityClassLabelsForKNN(self, knn, train_data, train_result):
        class_labels = dict()
        for i in range(len(knn)):
            sample_idx = knn[i]
            label = self.train_result[sample_idx]
            if label not in class_labels:
                class_labels[label] = 0
            class_labels[label] += 1
        return max(class_labels.keys(), key = lambda key: class_labels[key])

    def predict(self, x, k=None):
        if k == None:
            k = self.k
        knn = self.findKNearestNeigbors(x, k)
        return self.getMajorityClassLabelsForKNN(knn, self.train_data, self.train_result)

    def predictAndScore(self, data, result, k=None):
        error = 0.0
        for i in range(len(data)):
            label = self.predict(data[i], k)
            if label != result[i]:
                error += 1.0
        error /= len(data)
        return error

    def fitPredictAndScore(self, train_data, train_result, test_data, test_result):
        self.train_data = train_data
        self.train_result = train_result
        self.calculatePairWiseDistanceForTrainSamples()
        cross_validation_error_for_each_k = self.doNFoldCrossValidationAndMeasureK()
        train_error_for_each_k = []
        test_error_for_each_k = []
        for k in self.possible_k_values:
            train_error = self.predictAndScore(train_data, train_result, k)
            train_error_for_each_k.append(train_error)
            test_error = self.predictAndScore(test_data, test_result, k)
            test_error_for_each_k.append(test_error)
        plotErrorForK(self.possible_k_values, cross_validation_error_for_each_k, train_error_for_each_k, test_error_for_each_k)