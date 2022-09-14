import numpy as np
import torch
import torchvision.transforms as transforms
import torchvision.transforms.functional as TF
import torchvision.datasets 
from torchvision.datasets import CIFAR10
from torch.utils.data import DataLoader
from torch.utils.data.sampler import SubsetRandomSampler
import random
import params as P
import utils
import os


# Function to compute mean value, std dev and zca matrix for data normalization and whitening on CIFAR10
def get_dataset_stats(limit):
	# DATA_STATS_FILE = P.STATS_FOLDER + '/cifar10_' + str(limit) + '.pt'
	# MEAN_KEY = 'mean'
	# STD_KEY = 'std'
	# ZCA_KEY = 'zca'
	
	# # Load statistics
	# stats = utils.load_dict(DATA_STATS_FILE) # Try to load stats from file
	# if stats is None: # Stats file does not exist --> Compute statistics
	# 	print("Computing statistics on dataset[0:" + str(limit) + "] (this might take a while)")
		
	# 	# Load dataset
	# 	cifar10 = CIFAR10(root=P.DATA_FOLDER, train=True, download=False) # Load CIFAR10 dataset
	# 	X = cifar10.data[0:limit] # X is M x N (M = limit: samples, N = 3072: variables per dataset sample)
		
	# 	# Normalize the data to [0 1] range
	# 	X = X / 255.
	# 	# Compute mean and st. dev. and normalize the data to zero mean and unit variance
	# 	mean = X.mean(axis=(0, 1, 2), keepdims=True)
	# 	std = X.std(axis=(0, 1, 2), keepdims=True)
	# 	X = (X - mean)/std
	# 	# Transpose image tensors dimensions in order to put channel dimension in pos. 1, as expected by pytorch
	# 	X = X.transpose(0, 3, 1, 2)
	# 	# Reshape image tensors from shape 32x32x3 to vectors of size 32*32*3=3072
	# 	X = X.reshape(limit, -1)
	# 	# Compute ZCA matrix
	# 	cov = np.cov(X, rowvar=False)
	# 	U, S, V = np.linalg.svd(cov)
	# 	SMOOTHING_CONST = 1e-1
	# 	zca = np.dot(U, np.dot(np.diag(1.0 / np.sqrt(S + SMOOTHING_CONST)), U.T))
		
	# 	# Save statistics
	# 	stats = {MEAN_KEY: mean.squeeze().tolist(), STD_KEY: std.squeeze().tolist(), ZCA_KEY: torch.from_numpy(zca).float()}
	# 	utils.save_dict(stats, DATA_STATS_FILE)
	print("some statistics :D")
	return [0.485, 0.456, 0.406], [0.229, 0.224, 0.225], None
		


class DataManager:
	def __init__(self, config):
		# Constants for data loading
		self.VAL_SET_SPLIT = config.VAL_SET_SPLIT
		self.BATCH_SIZE = config.BATCH_SIZE
		
		# Compute dataset statistics
		# mean, std, zca = get_dataset_stats(self.VAL_SET_SPLIT)
		mean=[0.485, 0.456, 0.406]
		std=[0.229, 0.224, 0.225]
		# Define transformations to be applied on the data
		
		# Basic transformations
		T = transforms.Compose([
			# transforms.RandomResizedCrop(224),
			# transforms.Resize(256),
			# transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
			# The first transform is ToTensor, which transforms the raw CIFAR10 data to a tensor in the form
			# [depth, width, height]. Additionally, pixel values are mapped from the range [0, 255] to the range [0, 1]
			transforms.ToTensor(),
			# The Normalize transform subtracts mean values from each channel (passed in the first tuple) and divides each
			# channel by std dev values (passed in the second tuple). In this case we bring each channel to zero mean and
			# unitary std dev, i.e. from range [0, 1] to [-1, 1]
			transforms.Normalize(mean, std)
		])
		# Add whitening transformation, if needed
		# if config.WHITEN_DATA: T = transforms.Compose([T, transforms.LinearTransformation(zca, torch.zeros(zca.size(1)))])
		
		self.T_train = T
		self.T_test = transforms.Compose([
			# transforms.Resize(256),
            # transforms.CenterCrop(224),

			# transforms.Resize(64),
            # transforms.CenterCrop(64),
			
			transforms.ToTensor(),
			transforms.Normalize(mean, std)
		])
			
		# Extra transformations for data augmentation
		# if config.AUGMENT_DATA:
		# 	T_augm = transforms.Compose([
		# 		transforms.RandomApply([transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1, hue=20 / 360)], p=0.5),
		# 		transforms.RandomApply([transforms.ColorJitter(saturation=1)], p=0.5),
		# 		transforms.RandomHorizontalFlip(),
		# 		transforms.Pad(8),
		# 		transforms.RandomApply([transforms.Lambda(lambda x: TF.resize(x, (48 + random.randint(-6, 6), 48 + random.randint(-6, 6))))], p=0.3),
		# 		transforms.RandomApply([transforms.RandomAffine(degrees=10, shear=10)], p=0.3),
		# 		transforms.CenterCrop(40),
		# 		transforms.RandomApply([transforms.RandomCrop(32)], p=0.5),
		# 		transforms.CenterCrop(32),
		# 	])
		# 	self.T_train = transforms.Compose([T_augm, self.T_train])
		
	
	# Methods for obtaining train, validation and test set
	
	def get_train(self):
		# Download the dataset, if necessary, and preprocess with the specified transformations
		# cifar10 = CIFAR10(root=P.DATA_FOLDER, train=True, download=True, transform=self.T_train)

		# data_train = torchvision.datasets.ImageNet(P.DATA_FOLDER, split='train', transform=self.T_train)

		# TODO: USE IDENTICAL ALEXNET ARCHITECTURE & CONVERGE 
		# TODO 2: CHECK LABEL LOADING (IT'S NOT USING THE METADATA FROM IMAGENET)

		data_train = torchvision.datasets.ImageFolder(os.path.join(P.DATA_FOLDER, 'train'), transform=self.T_train)
		# The sampler is needed to extract the specific portion of dataset that will be used for training
		
		# sampler = SubsetRandomSampler(range(self.VAL_SET_SPLIT))
		# train_sampler = torch.utils.data.distributed.DistributedSampler(data_train)
		train_sampler = None
		# Build a DataLoader allowing to fetch data from the dataset. This is the obj that will be returned to the caller


		# TODO: REMOVE THE :100 SANITY CHECK IN THE BELOW LINE!!!
		# print(data_train.shape)
		return DataLoader(data_train, batch_size=self.BATCH_SIZE, shuffle=(train_sampler is None),
        num_workers=P.NUM_WORKERS, pin_memory=True, sampler=train_sampler)
	
	def get_val(self):
		# If all the training batches are used for training, use test set for validation
		if self.VAL_SET_SPLIT >= P.IMAGENET_NUM_TRN_SAMPLES: return self.get_test()
		# Download the dataset, if necessary, and preprocess with the specified transformations
		# data_val = torchvision.datasets.ImageNet(root=P.DATA_FOLDER, split='val', transform=self.T_test)
		data_val = torchvision.datasets.ImageFolder(os.path.join(P.DATA_FOLDER, 'val', 'images'), transform=self.T_test)
		# The sampler is needed to extract another portion of dataset that will be used for validation
		# val_sampler = torch.utils.data.distributed.DistributedSampler(data_val)
		val_sampler = None
		# Build a DataLoader allowing to fetch data from the dataset. This is the obj that will be returned to the caller
		

		# TODO: REMOVE THE :100 SANITY CHECK IN THE BELOW LINE!!!


		return DataLoader(data_val, batch_size=self.BATCH_SIZE, shuffle=(val_sampler is None), num_workers=P.NUM_WORKERS)
	
	# def get_test(self):
	# 	# Download the dataset, if necessary, and preprocess with the specified transformations
	# 	cifar10 = CIFAR10(root=P.DATA_FOLDER, train=False, download=True, transform=self.T_test)
	# 	# A sampler is not needed for the test dataset, because CIFAR10 already provides it in a separate batch
	# 	# Build a DataLoader allowing to fetch data from the dataset. This is the obj that will be returned to the caller
	# 	return DataLoader(cifar10, batch_size=self.BATCH_SIZE, num_workers=P.NUM_WORKERS)
