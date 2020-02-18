import os
import sys
import h5py
import numpy as np

import torch
import torch.utils.data as data


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

def _get_data_files(list_filename):
    with open(list_filename) as f:
        return [line.rstrip()[5:] for line in f]

def _load_data_file(name):
    f = h5py.File(name)
    data = f['data'][:]
    label = f['label'][:]
    return data, label
    
class ModelNet40Dataset(data.Dataset):
    def __init__(self, num_points, root, transforms=None, split='train'):
        super().__init__()
        self.transforms = transforms
        root = os.path.abspath(root)
        self.folder = "modelnet40"
        self.data_dir = os.path.join(root, self.folder)

        self.split, self.num_points = split, num_points
        if self.split == 'train':
            self.files =  _get_data_files( \
                os.path.join(self.data_dir, 'train_files.txt'))
        elif self.split == 'test':
            self.files =  _get_data_files( \
                os.path.join(self.data_dir, 'test_files.txt'))

        point_list, label_list = [], []
        for f in self.files:
            points, labels = _load_data_file(os.path.join(root, self.files[-1]))
            print(labels)
            point_list.append(points)
            label_list.append(labels)
            print(label_list)

        self.points = np.concatenate(point_list, 0)
        self.labels = np.concatenate(label_list, 0)

    def __getitem__(self, idx):
        pt_idxs = np.arange(0, self.points.shape[1])   # 2048
        if self.split == 'train':
            np.random.shuffle(pt_idxs)
        
        current_points = self.points[idx, pt_idxs].copy()
        label = torch.from_numpy(self.labels[idx]).type(torch.LongTensor)
        
        if self.transforms is not None:
            current_points = self.transforms(current_points)
        
        current_points = torch.transpose(current_points, 1, 0)
        
        return current_points, label

    def __len__(self):
        return self.points.shape[0]


class UnlabeledModelNet40Dataset(data.Dataset):
    def __init__(self, num_points, root, transforms=None, split='unlabeled'):
        super().__init__()
        self.transforms = transforms
        root = os.path.abspath(root)
        self.folder = "modelnet40"
        self.data_dir = os.path.join(root, self.folder)

        self.split, self.num_points = split, num_points
        if self.split == 'unlabeled':
            self.files =  _get_data_files( \
                os.path.join(self.data_dir, 'unlabeled_files.txt'))

        point_list = []
        for f in self.files:
            points, _ = _load_data_file(os.path.join(root, self.files[-1]))
            point_list.append(points)

        self.points = np.concatenate(point_list, 0)

    def __getitem__(self, idx):
        pt_idxs = np.arange(0, self.points.shape[1])
        
        current_points = self.points[idx, pt_idxs].copy()
        
        if self.transforms is not None:
            current_points = self.transforms(current_points)
        
        current_points = torch.transpose(current_points, 1, 0)
        
        return current_points

    def __len__(self):
        return self.points.shape[0]


if __name__ == "__main__":
    from torchvision import transforms
    import ClassArch.utils.data_utils as d_utils

    transforms = transforms.Compose([
        # d_utils.PointcloudToTensor(),
        # d_utils.PointcloudRotatebyAngle(rotation_angle=40),
        # d_utils.PointcloudScale(),
        # d_utils.PointcloudTranslate(),
        # d_utils.PointcloudJitter()
    ])
    dset = ModelNet40Dataset(16, "./data", split='train', transforms=transforms)
    print(dset[0][0])
    print(dset[0][1])
    print(len(dset))
    dloader = torch.utils.data.DataLoader(dset, batch_size=32, shuffle=True)