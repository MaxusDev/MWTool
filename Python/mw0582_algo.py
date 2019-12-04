import numpy as np

def movingAverage(data, exp, avg):
  new_avg = data * exp + (1 - exp) * avg
  return new_avg

def impulseRemoval(arr, size):
  m = np.mean(arr)
  for x in arr:
    if x > mean:
      pos = pos + 1
      diff = diff + x - mean
    elif x < mean:
      neg = neg + 1
  correct = mean + (pos - neg) * diff / size**2
  return correct

def dcRemoval(data, exp, avg):
  new_avg = data * exp + (1 - exp) * avg
  base = data - new_avg
  return base, new_avg

def envelopExtract(data, w_dc, w_env, avg, env_avg):
    base, new_dc_avg = dcRemoval(data, w_dc, avg)
    new_env_avg = movingAverage(np.abs(base), w_env, env_avg)
    return new_dc_avg, new_env_avg

