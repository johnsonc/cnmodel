import os
import numpy as np
from ..util import matlab_proc

_proc = None

def get_matlab():
    """ Return a running MatlabProcess instance.
    """
    global _proc
    if _proc is None:
        path = os.path.dirname(__file__)
        model_path = os.path.join(path, 'model')
        _proc = matlab_proc.MatlabProcess(cwd=model_path)
    return _proc


def model_ihc(pin, CF, nrep=1, tdres=1e-5, reptime=1, cohc=1, cihc=1, species=1, **kwds):
    """
    Return the output of model_IHC() from the AN model
    (Zilany, Bruce, Ibrahim and Carney, 2014; requires MATLAB)
    
    This function takes a sound waveform as input and models a single inner 
    hair cell (IHC). The return values is the IHC potential in volts.
    
    Parameters
    ----------
    pin : array
        The input sound wave in Pa sampled at the rate specified by *tdres*
    CF : float
        The characteristic frequency of the IHC in Hz
    nrep : int
        The number of times to repeat the stimulus
    tdres : float
        The binsize in seconds, i.e., the reciprocal of the sampling rate
    reptime : float
        The time between stimulus repetitions in seconds. 
        NOTE should be equal to or longer than the duration of pin
    cohc : float
        The OHC scaling factor: 1 is normal OHC function; 
        0 is complete OHC dysfunction
    cihc : float
        The IHC scaling factor: 1 is normal IHC function; 
        0 is complete IHC dysfunction
    species : int
        The model species: "1" for cat, "2" for human with BM tuning from 
        Shera et al. (PNAS 2002), or "3" for human BM tuning from 
        Glasberg & Moore (Hear. Res. 1990)
    """
    # make sure pin is a row vector
    pin = pin.reshape(1, pin.size)
    
    # convert all args to double, as required by model_IHC
    args = [pin]
    for arg in (CF, nrep, tdres, reptime, cohc, cihc, species):
        if not isinstance(arg, matlab_proc.MatlabReference):
            arg = float(arg)
        args.append(arg)
        
    assert reptime >= pin.size * tdres
    
    ml = get_matlab()
    fn = ml.model_IHC
    fn.nargout = 1  # necessary because nargout(model_IHC) fails
    return fn(*args, **kwds)


def model_synapse(vihc, CF, nrep=1, tdres=1e-5, fiberType=0, noiseType=1, implnt=1, **kwds):
    """
    Return the output of model_Synapse() from the AN model
    (Zilany, Bruce, Ibrahim and Carney, 2014; requires MATLAB)
    
    This function takes an IHC voltage waveform as input (see model_ihc) and 
    models a synapse and spiral ganglion cell. The return values are:
    
    * meanrate: The estimated instantaneous mean rate (incl. refractoriness)
    * varrate: The estimated instantaneous variance in the discharge rate (incl. refractoriness)
    * psth: The peri-stimulus time histogram 

    Parameters
    ----------
    vihc : array
        IHC voltage as generated by model_ihc()
    CF : float
        The characteristic frequency of the IHC in Hz
    nrep : int
        The number of times to repeat the stimulus
    tdres : float
        The binsize in seconds, i.e., the reciprocal of the sampling rate
    fiberType : int
        The type of the fiber based on spontaneous rate (SR) in spikes/s:
        1 for Low SR; 2 for Medium SR; 3 for High SR
    noiseType : 0 or 1
        Fixed fGn (noise will be same in every simulation) or variable fGn: 
        "0" for fixed fGn and "1" for variable fGn
    implnt : 0 or 1
        "Approxiate" or "actual" implementation of the power-law functions: 
        "0" for approx. and "1" for actual implementation
    """
    # make sure vihc is a row vector (unless it is a reference to a matlab variable)
    if isinstance(vihc, np.ndarray):
        vihc = vihc.reshape(1, vihc.size)

    # convert all args to double, as required by model_Synapse
    args = [vihc]
    for arg in (CF, nrep, tdres, fiberType, noiseType, implnt):
        if not isinstance(arg, matlab_proc.MatlabReference):
            arg = float(arg)
        args.append(arg)
    
    ml = get_matlab()
    fn = ml.model_Synapse
    fn.nargout = 3  # necessary because nargout(model_IHC) fails
    return fn(*args, **kwds)
    

def seed_rng(seed):
    """
    Seed the random number generator used by model_ihc and model_synapse. 
    """
    seed = int(seed)
    cmd = "RandStream.setGlobalStream(RandStream('mcg16807','seed',%d));" % seed
    ml = get_matlab()
    ml(cmd)
