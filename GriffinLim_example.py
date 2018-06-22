#!/usr/bin/env python
# -*- encoding: utf-8 -*-
__author__ = 'Feiteng'
import scipy
import shutil

import numpy as np
import librosa
from librosa import display
from optparse import OptionParser
from matplotlib import pyplot as plt


def griffin_lim(stftm_matrix, shape, min_iter=20, max_iter=50, delta=20):
  y = np.random.random(shape)
  y_iter = []

  for i in range(max_iter):
    if i >= min_iter and (i - min_iter) % delta == 0:
      y_iter.append((y, i))
    stft_matrix = librosa.core.stft(y)
    stft_matrix = stftm_matrix * stft_matrix / np.abs(stft_matrix)
    y = librosa.core.istft(stft_matrix)
  y_iter.append((y, max_iter))

  return y_iter


if __name__ == '__main__':
  cmd_parser = OptionParser(usage="usage: %prog <wav-file>")

  cmd_parser.parse_args()
  (opts, argv) = cmd_parser.parse_args()

  if len(argv) != 1:
    cmd_parser.print_help()
    exit(-1)

  np.random.seed(0)
  # assume 1 channel wav file
  sr, data = scipy.io.wavfile.read(argv[0])

  stftm_matrix = np.abs(librosa.core.stft(data))
  stftm_matrix_modified = stftm_matrix + np.random.random(stftm_matrix.shape)

  y_iters = griffin_lim(stftm_matrix_modified, data.shape)
  n_figure = 1 + len(y_iters)

  plt.figure(figsize=(8, 14))
  plt.subplot(n_figure, 1, 1)
  display.waveplot(data, sr=sr)
  plt.title('origin wave')

  for i in range(0, len(y_iters)):
    y, n_iters = y_iters[i]
    print('NumIters {}'.format(n_iters))
    plt.subplot(n_figure, 1, i + 2)
    display.waveplot(y.astype(np.int16), sr=sr)
    plt.title('reconstructed wave from STFT-M (Iter {})'.format(n_iters))
    store_file = argv[0].replace('.wav', '_stftm_reconstruct_iters{iters}.wav'.format(iters=n_iters))
    shutil.rmtree(store_file, ignore_errors=True)
    scipy.io.wavfile.write(store_file, sr, y.astype(np.int16))

  plt.savefig(argv[0].replace('.wav', '.png'), dpi=100)

  print('DONE')
