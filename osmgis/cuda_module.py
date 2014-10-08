#!/usr/bin/env python
import time
from functools import wraps
import cython
import pycuda.autoinit
import pycuda.driver as cuda
import pycuda.gpuarray as gpuarray
from pycuda.compiler import SourceModule
import numpy as np
import pandas as pd

def single_precision_df(fn):
    @wraps(fn)
    def wrap(*args,**kwargs):
        df =  fn(*args,**kwargs)
        # cast to np.float32
        return df
    return wrap

class CUDA_Module:
    def _module_prototype(self, name, inputs, script):
        func = """
        __global__ void %(name)s ( %(inputs)s )
        {
            %(script)s
        }
        """
        return func % dict(name=name, inputs=inputs, script=script) 

    @classmethod
    def copy_to_gpu(cls, arr):
        arr_gpu = cuda.mem_alloc(arr.nbytes)
        cuda.memcpy_htod(arr_gpu, arr)
        return arr_gpu

    @classmethod
    def copy_from_gpu(cls,empty,arr_gpu):
        cuda.memcpy_dtoh(empty,arr_gpu)
        return empty

    def get_function(self, name):
        """get the module function"""
        return self.mod.get_function(name)

    def gpu_function(fn):
        @wraps(fn)
        def wrap(self, arr, block=None, **kwargs):
            """input arr is the numpy array of data, block is 1x3 tuple of block used,
            while **kwargs is the input to the decrated function
            returns value calculated by the cuda module"""
            inputs,script = fn(self, **kwargs)
            mod = self._module_prototype(fn.__name__, inputs, script)
            self.mod = SourceModule(mod)
            func = self.get_function(fn.__name__)
            if block is None:
                block = arr.shape
                while len(block)<3:
                    block += (1,)
            func(cuda.InOut(arr),block)
            return arr
        return wrap

class cudaSeries(pd.Series):
    def to_cuda(self):
        arr = np.array(self)
        if arr.dtype==np.float64:
            arr = arr.astype(np.float32)
        return gpuarray.to_gpu(arr)

class cudaDataFrame(pd.DataFrame):
    def to_cuda(self):
        arr = self[self.dtypes!=np.object]
        # possibly change this so that only one type is accepted since I doubt cuda can handle many types per thread block
        arr[arr.dtypes==np.float64] = arr[arr.dtypes==np.float64].astype(np.float32)
        arr = np.array(arr)
        return gpuarray.to_gpu(arr)




