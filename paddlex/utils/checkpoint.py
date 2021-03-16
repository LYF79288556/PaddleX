# Copyright (c) 2021 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import os.path as osp
import paddle
from paddle.static import load_program_state
import paddlex.utils.logging as logging
from .download import download_and_decompress

cityscapes_weights = {
    'UNet_CITYSCAPES':
    'https://bj.bcebos.com/paddleseg/dygraph/cityscapes/unet_cityscapes_1024x512_80k/model.pdparams'
}

imagenet_weights = {
    'ResNet18_IMAGENET':
    'https://paddle-imagenet-models-name.bj.bcebos.com/dygraph/ResNet18_pretrained.pdparams',
    'ResNet34_IMAGENET':
    'https://paddle-imagenet-models-name.bj.bcebos.com/dygraph/ResNet34_pretrained.pdparams',
    'ResNet50_IMAGENET':
    'https://paddle-imagenet-models-name.bj.bcebos.com/dygraph/ResNet50_pretrained.pdparams',
    'ResNet101_IMAGENET':
    'https://paddle-imagenet-models-name.bj.bcebos.com/dygraph/ResNet101_pretrained.pdparams',
    'ResNet152_IMAGENET':
    'https://paddle-imagenet-models-name.bj.bcebos.com/dygraph/ResNet101_pretrained.pdparams'
}


def get_pretrained_weights(flag, class_name, save_dir):
    if flag is None:
        return None
    elif osp.isdir(flag):
        return flag
    elif osp.isfile(flag):
        return flag

    # TODO: check flag
    new_save_dir = save_dir
    weights_key = "{}_{}".format(class_name, flag)
    if flag == 'CITYSCAPES':
        url = cityscapes_weights[weights_key]
    elif flag == 'IMAGENET':
        url = imagenet_weights[weights_key]
    else:
        pass
    fname = download_and_decompress(url, path=new_save_dir)
    return fname


def load_pretrained_weights(model,
                            pretrained_weights=None,
                            load_static_weights=False):
    if pretrained_weights is not None:
        logging.info(
            'Loading pretrained model from {}'.format(pretrained_weights),
            use_color=True)

        if os.path.exists(pretrained_weights):
            if load_static_weights:
                para_state_dict = load_program_state(pretrained_weights)
                # param_state_dict = {}
                # model_state_dict = model.state_dict()
                # for k in model_state_dict:
                #     weight_name = model_state_dict[k].name
                #     if weight_name in para_state_dict:
                #         logging.info('Load weight: {}, shape: {}'.format(
                #             weight_name, para_state_dict[weight_name].shape))
                #         param_state_dict[k] = para_state_dict[weight_name]
                #     else:
                #         param_state_dict[k] = model_state_dict[k]
                # model.set_dict(param_state_dict)
            else:
                para_state_dict = paddle.load(pretrained_weights)
            model_state_dict = model.state_dict()
            keys = model_state_dict.keys()
            num_params_loaded = 0
            for k in keys:
                if k not in para_state_dict:
                    logging.warning("{} is not in pretrained model".format(k))
                elif list(para_state_dict[k].shape) != list(model_state_dict[k]
                                                            .shape):
                    logging.warning(
                        "[SKIP] Shape of pretrained params {} doesn't match.(Pretrained: {}, Actual: {})"
                        .format(k, para_state_dict[k].shape, model_state_dict[
                            k].shape))
                else:
                    model_state_dict[k] = para_state_dict[k]
                    num_params_loaded += 1
            model.set_dict(model_state_dict)
            logging.info("There are {}/{} variables loaded into {}.".format(
                num_params_loaded,
                len(model_state_dict), model.__class__.__name__))
        else:
            raise ValueError('The pretrained model directory is not Found: {}'.
                             format(pretrained_weights))
    else:
        logging.info(
            'No pretrained model to load, {} will be trained from scratch.'.
            format(model.__class__.__name__))
