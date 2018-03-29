#!/usr/bin/python
# coding:utf-8
from sklearn.externals import joblib
import numpy as np
import matplotlib.pyplot as plt
import pylab as pl
import scipy.stats as stats
import os
import ConfigParser
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.font_manager import FontProperties


# read conf file
file_path = os.path.dirname(__file__)
cp_models = ConfigParser.SafeConfigParser()
cp_models.read(os.path.join(file_path, '../cfg/models.cfg'))
# the datasets path
datasets_path = os.path.join(file_path, cp_models.get('datasets', 'path'))

# load datasets
ipromps_set = joblib.load(os.path.join(datasets_path, 'pkl/ipromps_set.pkl'))
# ipromps_set_post = joblib.load(os.path.join(datasets_path, 'pkl/ipromps_set_post.pkl'))
datasets_norm_preproc = joblib.load(os.path.join(datasets_path, 'pkl/datasets_norm_preproc.pkl'))
datasets_norm = joblib.load(os.path.join(datasets_path, 'pkl/datasets_norm.pkl'))
datasets_raw = joblib.load(os.path.join(datasets_path, 'pkl/datasets_raw.pkl'))
datasets_filtered = joblib.load(os.path.join(datasets_path, 'pkl/datasets_filtered.pkl'))
task_name = joblib.load(os.path.join(datasets_path, 'pkl/task_name_list.pkl'))
# [robot_traj_offline, ground_truth] = joblib.load(os.path.join(datasets_path, 'pkl/robot_traj_offline.pkl'))
# robot_traj_online = joblib.load(os.path.join(datasets_path, 'pkl/robot_traj_online.pkl'))
# obs_data_online = joblib.load(os.path.join(datasets_path, 'pkl/obs_data_online.pkl'))



# read datasets cfg file
cp_datasets = ConfigParser.SafeConfigParser()
cp_datasets.read(os.path.join(datasets_path, 'info/cfg/datasets.cfg'))
# read datasets params
data_index_sec = cp_datasets.items('index_15')
data_index = [map(int, task[1].split(',')) for task in data_index_sec]

# the idx of interest info in data structure
info_n_idx = {
            'left_hand': [0, 3],
            'left_joints': [3, 6]
            }
# the info to be plotted
info = cp_models.get('visualization', 'info')
joint_num = info_n_idx[info][1] - info_n_idx[info][0]
num_obs = cp_models.getint('visualization', 'num_obs')


# zh config
def conf_zh(font_name):
    from pylab import mpl
    mpl.rcParams['font.sans-serif'] = [font_name]
    mpl.rcParams['axes.unicode_minus'] = False


# plot the raw data
def plot_raw_data(num=0):
    for task_idx, ipromps_idx in enumerate(ipromps_set):
        fig = plt.figure(task_idx + num)
        fig.suptitle('the raw data of ' + info)
        for demo_idx in range(ipromps_idx.num_demos):
            for joint_idx in range(joint_num):
                ax = fig.add_subplot(joint_num, 1, 1 + joint_idx)
                data = datasets_raw[task_idx][demo_idx][info][:, joint_idx]
                plt.plot(np.array(range(len(data)))/100.0, data)
                ax.set_xlabel(u'时间/秒')
                ax.set_ylabel(u'位移/米')

# plot the norm data
def plot_norm_data(num=0):
    for task_idx, ipromps_idx in enumerate(ipromps_set):
        fig = plt.figure(task_idx + num)
        fig.suptitle('the raw data of ' + info)
        for demo_idx in range(ipromps_idx.num_demos):
            for joint_idx in range(joint_num):
                ax = fig.add_subplot(joint_num, 1, 1 + joint_idx)
                data = datasets_norm[task_idx][demo_idx][info][:, joint_idx]
                plt.plot(np.array(range(len(data)))/100.0, data)
                ax.set_xlabel(u'时间/秒')
                ax.set_ylabel(u'位移/米')

# plot the filtered data
def plot_filtered_data(num=0):
    for task_idx, ipromps_idx in enumerate(ipromps_set):
        fig = plt.figure(task_idx + num)
        fig.suptitle('the filtered data of ' + info)
        for demo_idx in range(ipromps_idx.num_demos):
            for joint_idx in range(joint_num):
                ax = fig.add_subplot(joint_num, 1, 1 + joint_idx)
                data = datasets_filtered[task_idx][demo_idx][info][:, joint_idx]
                plt.plot(np.array(range(len(data)))/100.0, data, )
                ax.set_xlabel(u'时间/秒')
                ax.set_ylabel(u'位移/米')
                plt.legend()


# plot the prior distribution
def plot_prior(num=0):
    for task_idx, ipromps_idx in enumerate(ipromps_set):
        fig = plt.figure(task_idx+num)
        fig.suptitle('the prior of ' + info + ' for ' + task_name[task_idx] + ' model')
        for joint_idx in range(joint_num):
            ax = fig.add_subplot(joint_num, 1, 1+joint_idx)
            ipromps_idx.promps[joint_idx + info_n_idx[info][0]].plot_prior(b_regression=True)


# plot alpha distribute
def plot_alpha(num=0):
    fig = plt.figure(num)
    for idx, ipromp in enumerate(ipromps_set):
        ax = fig.add_subplot(len(ipromps_set), 1, 1+idx)
        h = ipromps_set[idx].alpha
        h.sort()
        h_mean = np.mean(h)
        h_std = np.std(h)
        pdf = stats.norm.pdf(h, h_mean, h_std)
        pl.hist(h, normed=True, color='b')
        plt.plot(h, pdf, linewidth=5, color='r', marker='o', markersize=10)
        # candidate = ipromp.alpha_candidate()
        # candidate_x = [x['candidate'] for x in candidate]
        # prob = [x['prob'] for x in candidate]
        # plt.plot(candidate_x, prob, linewidth=0, color='g', marker='o', markersize=14)


# plot the post distribution
def plot_post(num=0):
    for task_idx, ipromps_idx in enumerate(ipromps_set_post):
        fig = plt.figure(task_idx+num)
        for joint_idx in range(joint_num):
            ax = fig.add_subplot(joint_num, 1, 1 + joint_idx)
            ipromps_idx.promps[joint_idx + info_n_idx[info][0]].plot_nUpdated(color='r', via_show=True)


# plot the generated robot motion trajectory
def plot_robot_traj(num=0):
    fig = plt.figure(num)
    fig.suptitle('predict robot motion')
    for joint_idx in range(7):
        ax = fig.add_subplot(7, 1, 1 + joint_idx)
        plt.plot(np.linspace(0, 1.0, 101), robot_traj_online[:, joint_idx])


# plot the raw data index
def plot_raw_data_index(num=0):
    for task_idx, demo_list in enumerate(data_index):
        for demo_idx in demo_list:
            fig = plt.figure(num + task_idx)
            fig.suptitle('the raw data of ' + info)
            for joint_idx in range(joint_num):
                ax = fig.add_subplot(joint_num, 1, 1 + joint_idx)
                data = datasets_raw[task_idx][demo_idx][info][:, joint_idx]
                plt.plot(range(len(data)), data, label=str(demo_idx))
                plt.legend()


# plot the filter data index
def plot_filter_data_index(num=0):
    for task_idx, demo_list in enumerate(data_index):
        for demo_idx in demo_list:
            fig = plt.figure(num + task_idx)
            fig.suptitle('the raw data of ' + info)
            for joint_idx in range(joint_num):
                ax = fig.add_subplot(joint_num, 1, 1 + joint_idx)
                data = datasets_filtered[task_idx][demo_idx][info][:, joint_idx]
                plt.plot(range(len(data)), data, label=str(demo_idx))
                ax.legend()


# plot the 3d raw traj
def plot_3d_raw_traj(num=0):
    for task_idx, demo_list in enumerate(data_index):
        fig = plt.figure(task_idx + num)
        ax = fig.gca(projection='3d')
        for demo_idx in demo_list:
            for joint_idx in range(joint_num):
                data = datasets_raw[task_idx][demo_idx][info]
                ax.plot(data[:, 0], data[:, 1], data[:, 2], label=str(demo_idx))
                ax.set_xlabel('X Label')
                ax.set_ylabel('Y Label')
                ax.set_zlabel('Z Label')
                ax.legend()


# plot the 3d filtered traj
def plot_3d_filtered_h_traj(num=0):
    for task_idx, demo_list in enumerate(data_index):
        fig = plt.figure(task_idx+num)
        ax = fig.gca(projection='3d')
        for demo_idx in demo_list:
            data = datasets_filtered[task_idx][demo_idx]['left_hand']
            ax.plot(data[:, 0], data[:, 1], data[:, 2], linewidth=2,
                    # label='training sets about human '+str(demo_idx), alpha=0.3)
                    alpha=1.0)
            ax.set_xlabel('X Label')
            ax.set_ylabel('Y Label')
            ax.set_zlabel('Z Label')
            ax.legend()


# plot the offline obs
def plot_offline_3d_obs(num=0):
    for task_idx, demo_list in enumerate(data_index):
        fig = plt.figure(task_idx + num)
        ax = fig.gca(projection='3d')
        obs_data_dict = ground_truth
        data = obs_data_dict['left_hand']
        ax.plot(data[0:num_obs, 0], data[0:num_obs, 1], data[0:num_obs, 2],
                # 'o', markersize=10, label='observation points', alpha=1.0, color='green')
                'o', markersize = 12, label = u'人运动的观测点', alpha = 1.0, color = 'green')
        ax.plot(data[:, 0], data[:, 1], data[:, 2],
                # '-', linewidth=5, color='blue', label='ground truth human trajectory', alpha=1.0)
                '-', linewidth = 5, color = 'blue', label = u'人运动轨迹的真实值', alpha = 1.0)
        # ax.set_xlabel('X Label')
        # ax.set_ylabel('Y Label')
        # ax.set_zlabel('Z Label')
        ax.legend()


# plot the 3d filtered robot traj
def plot_3d_filtered_r_traj(num=0):
    for task_idx, demo_list in enumerate(data_index):
        fig = plt.figure(task_idx+num)
        ax = fig.gca(projection='3d')
        for demo_idx in demo_list:
            data = datasets_filtered[task_idx][demo_idx]['left_joints']
            ax.plot(data[:, 0], data[:, 1], data[:, 2],
                    # linewidth=3, linestyle='-', label='training sets about robot '+str(demo_idx), alpha=0.3)
                    linewidth=2, linestyle='-', alpha=1.0)
            # ax.set_xlabel('X Label')
            # ax.set_ylabel('Y Label')
            # ax.set_zlabel('Z Label')
            ax.set_xlabel(u'X/米')
            ax.set_ylabel(u'Y/米')
            ax.set_zlabel(u'Z/米')
            ax.legend()


# plot the 3d generated robot traj
def plot_gen_3d_offline_r_traj(num=0):
    for task_idx, demo_list in enumerate(data_index):
        fig = plt.figure(task_idx+num)
        ax = fig.gca(projection='3d')
        data = robot_traj_offline
        ax.plot(data[:, 0], data[:, 1], data[:, 2],
                # linewidth=5, linestyle='--', label='generated robot trajectory')
                linewidth = 5, linestyle = '--', label = u'生成的机器人运动轨迹')
        data = ground_truth['left_joints']
        ax.plot(data[:, 0], data[:, 1], data[:, 2],
                # linewidth=5, linestyle='-', color='r', label='ground truth robot trajectory', alpha=1.0)
                linewidth=5, linestyle='-', color='r', label=u'机器人运动轨迹的真实值', alpha=1.0)
        ax.set_xlabel(u'X/米')
        ax.set_ylabel(u'Y/米')
        ax.set_zlabel(u'Z/米')
        ax.legend()


# plot the 3d generated robot traj
def plot_gen_3d_online_r_traj(num=0):
    for task_idx, demo_list in enumerate(data_index):
        fig = plt.figure(task_idx+num)
        ax = fig.gca(projection='3d')
        data = robot_traj_online
        ax.plot(data[:, 0], data[:, 1], data[:, 2],
                linewidth=8, linestyle='-', label='generated online robot traj', alpha=0.2)
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
        ax.legend()


def plot_online_3d_obs(num):
    for task_idx, demo_list in enumerate(data_index):
        fig = plt.figure(task_idx + num)
        ax = fig.gca(projection='3d')
        data = obs_data_online
        ax.plot(data[0:num_obs, 0], data[0:num_obs, 1], data[0:num_obs, 2],
                'o', linewidth=3, label='obs points', alpha=0.2)
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
        ax.legend()


# plot offline test pair
def pairs_offline(num=0):
    plot_3d_filtered_h_traj(num)
    plot_3d_filtered_r_traj(num)
    # plot_offline_3d_obs(num)
    # plot_gen_3d_offline_r_traj(num)


# plot online test pair
def pairs_online(num=0):
    plot_3d_filtered_h_traj(num)
    plot_3d_filtered_r_traj(num)
    plot_online_3d_obs(num)
    plot_gen_3d_online_r_traj(num)


def main():
    conf_zh("Droid Sans Fallback")
    # plt.close('all')
    # plot_raw_data(0)
    # plot_norm_data(2)
    plot_filtered_data(1)
    # plot_prior(1)
    # plot_post()
    # plot_alpha()
    # plot_robot_traj()
    # plot_raw_data_index()
    # plot_filter_data_index(20)

    #3D
    # plot_3d_raw_traj(10)
    # plot_3d_gen_r_traj_online(10)
    # pairs_offline(10)
    # pairs_online(10)
    # plt.legend(prop = {'size': 20})
    plt.show()


if __name__ == '__main__':
    main()
