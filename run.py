import os
import argparse
import random
import json
import numpy as np
import torch
from args import Configs
import logging
from sklearn.model_selection import train_test_split
import tarfile
import os.path




from models import TReS, Net


print('torch version: {}'.format(torch.__version__))


def main(config): 
    os.environ['CUDA_VISIBLE_DEVICES'] = config.gpunum
    config.ngpus = len( list(map(int, config.gpunum.split(','))) )
    
    folder_path = {
        'live':     config.datapath,
        'csiq':     config.datapath,
        'tid2013':  config.datapath,
        'kadid10k': config.datapath,
        'clive':    config.datapath,
        'koniq':    config.datapath,
        'fblive':   config.datapath,
        'spaq':     config.datapath,
        'biq':      config.datapath,
        'pipal':    config.datapath
        }

    img_num = {
        'live':     list(range(0, 29)),
        'csiq':     list(range(0, 30)),
        'kadid10k': list(range(0, 80)),
        'tid2013':  list(range(0, 25)),
        'clive':    list(range(0, 1169)),
        'koniq':    list(range(0, 10073)),
        'fblive':   list(range(0, 39810)),
        'spaq':     list(range(0, 11125)),
        'biq':      list(range(0, 11989)),
        'pipal':    list(range(0, 200))
        }
    

    print('Training and Testing on {} dataset...'.format(config.dataset))
    


    
    SavePath = config.svpath
    svPath = SavePath+ config.dataset + '_' + str(config.vesion)+'_'+str(config.seed)+'/'+'sv'
    print(svPath)
    os.makedirs(svPath, exist_ok=True)
        
    
    
     # fix the seed if needed for reproducibility
    if config.seed == 0:
        pass
    else:
        print('we are using the seed = {}'.format(config.seed))
        torch.manual_seed(config.seed)
        torch.cuda.manual_seed(config.seed)
        np.random.seed(config.seed)
        random.seed(config.seed)

    total_num_images = img_num[config.dataset]
    
    
    # Randomly select 80% images for training and the rest for testing
    # random.shuffle(total_num_images)
    # train_index = total_num_images[0:int(round(0.8 * len(total_num_images)))]
    # test_index = total_num_images[int(round(0.8 * len(total_num_images))):len(total_num_images)]

    train_index, test_index = train_test_split(total_num_images, test_size=0.2, random_state=config.seed)
    val_index, test_index = train_test_split(test_index, test_size=0.5, random_state=config.seed)

    imgsTrainPath = svPath + '/' + 'train_index_'+str(config.vesion)+'_'+str(config.seed)+'.json'
    imgsValPath = svPath + '/' + 'val_index_'+str(config.vesion)+'_'+str(config.seed)+'.json'
    imgsTestPath = svPath + '/' + 'test_index_'+str(config.vesion)+'_'+str(config.seed)+'.json'
    

    with open(imgsTrainPath, 'w') as json_file2:
        json.dump( train_index, json_file2)
    with open(imgsValPath, 'w') as json_file2:
        json.dump( val_index, json_file2)
    with open(imgsTestPath, 'w') as json_file2:
        json.dump( test_index, json_file2)



    solver = TReS(config, svPath, folder_path[config.dataset], train_index, val_index, Net)
    srcc_computed, plcc_computed = solver.train(config.seed,svPath)
    
    
    
    # logging the performance
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    handler = logging.FileHandler(svPath + '/LogPerformance.log')

    formatter    = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    Dataset = config.dataset
    logger.info(Dataset)
    
    PrintToLogg = 'Best val PLCC: {}, SROCC: {}'.format(plcc_computed, srcc_computed)
    logger.info(PrintToLogg)
    logger.info('---------------------------')

    with tarfile.open(f"{(config.svpath).split('Save_TReS')[0]}output.tar.gz", "w:gz") as tar:
        tar.add(config.svpath, arcname=os.path.basename(config.svpath))

if __name__ == '__main__':
    
    config = Configs()
    print(config)
        
    main(config)
    
