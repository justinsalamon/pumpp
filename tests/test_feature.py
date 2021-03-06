#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''Tests for first-level audio feature extraction'''

import numpy as np
import pytest
import librosa

import pumpp

from test_task import shape_match, type_match


@pytest.fixture(params=[None, 22050, 16000], scope='module')
def audio(request):
    y, sr_out = librosa.load(librosa.util.example_audio_file(),
                             sr=request.param,
                             duration=5)
    return {'y': y, 'sr': sr_out}


@pytest.fixture(params=[512, 1024])
def n_fft(request):
    return request.param


@pytest.fixture(params=[32, 128])
def n_mels(request):
    return request.param


@pytest.fixture()
def SR():
    return 22050


@pytest.fixture()
def HOP_LENGTH():
    return 512


@pytest.fixture(params=[192, 384])
def WIN_LENGTH(request):
    return request.param


@pytest.fixture(params=[16, 128])
def N_FMT(request):
    return request.param


@pytest.fixture(params=[1, 3])
def over_sample(request):
    return request.param


@pytest.fixture(params=[1, 4])
def n_octaves(request):
    return request.param


@pytest.fixture(params=[None, 'tf', 'th', 'channels_last', 'channels_first',
                        pytest.mark.xfail('bad mode',
                                          raises=pumpp.ParameterError)])
def conv(request):
    return request.param


@pytest.fixture(params=[False, True])
def log(request):
    return request.param


@pytest.fixture(params=['tf', 'th', 'channels_last', 'channels_first',
                        pytest.mark.xfail(None,
                                          raises=pumpp.ParameterError),
                        pytest.mark.xfail('bad mode',
                                          raises=pumpp.ParameterError)])
def hconv(request):
    return request.param


@pytest.fixture(params=[None, [1], [1, 2], [1, 2, 3],
                        pytest.mark.xfail([-1], raises=pumpp.ParameterError),
                        pytest.mark.xfail('bad harmonics',
                                          raises=pumpp.ParameterError)])
def harmonics(request):
    return request.param


# STFT features
def __check_shape(fields, key, dim, conv, channels=1):

    if conv is None:
        assert fields[key].shape == (None, dim)
    elif conv in ('channels_last', 'tf'):
        assert fields[key].shape == (None, dim, channels)
    elif conv in ('channels_first', 'th'):
        assert fields[key].shape == (channels, None, dim)


def test_feature_stft_fields(SR, HOP_LENGTH, n_fft, conv, log):

    ext = pumpp.feature.STFT(name='stft',
                             sr=SR, hop_length=HOP_LENGTH,
                             n_fft=n_fft,
                             conv=conv)

    # Check the fields
    assert set(ext.fields.keys()) == set(['stft/mag', 'stft/phase'])

    __check_shape(ext.fields, 'stft/mag', 1 + n_fft // 2, conv)
    __check_shape(ext.fields, 'stft/phase', 1 + n_fft // 2, conv)
    assert ext.fields['stft/mag'].dtype is np.float32
    assert ext.fields['stft/phase'].dtype is np.float32


def test_feature_stft_mag_fields(SR, HOP_LENGTH, n_fft, conv):

    ext = pumpp.feature.STFTMag(name='stft',
                                sr=SR, hop_length=HOP_LENGTH,
                                n_fft=n_fft,
                                conv=conv)

    # Check the fields
    assert set(ext.fields.keys()) == set(['stft/mag'])

    __check_shape(ext.fields, 'stft/mag', 1 + n_fft // 2, conv)
    assert ext.fields['stft/mag'].dtype is np.float32


def test_feature_stft_phasediff_fields(SR, HOP_LENGTH, n_fft, conv):

    ext = pumpp.feature.STFTPhaseDiff(name='stft',
                                      sr=SR, hop_length=HOP_LENGTH,
                                      n_fft=n_fft,
                                      conv=conv)

    # Check the fields
    assert set(ext.fields.keys()) == set(['stft/mag', 'stft/dphase'])

    __check_shape(ext.fields, 'stft/mag', 1 + n_fft // 2, conv)
    __check_shape(ext.fields, 'stft/dphase', 1 + n_fft // 2, conv)
    assert ext.fields['stft/mag'].dtype is np.float32
    assert ext.fields['stft/dphase'].dtype is np.float32


def test_feature_stft(audio, SR, HOP_LENGTH, n_fft, conv, log):

    ext = pumpp.feature.STFT(name='stft',
                             sr=SR, hop_length=HOP_LENGTH,
                             n_fft=n_fft,
                             conv=conv)

    output = ext.transform(**audio)

    assert set(output.keys()) == set(ext.fields.keys())

    for key in ext.fields:
        assert shape_match(output[key].shape[1:], ext.fields[key].shape)
        assert type_match(output[key].dtype, ext.fields[key].dtype)


def test_feature_stft_phasediff(audio, SR, HOP_LENGTH, n_fft, conv, log):

    ext = pumpp.feature.STFTPhaseDiff(name='stft',
                                      sr=SR, hop_length=HOP_LENGTH,
                                      n_fft=n_fft,
                                      conv=conv)

    output = ext.transform(**audio)

    # Check the fields
    assert set(output.keys()) == set(ext.fields.keys())

    for key in ext.fields:
        assert shape_match(output[key].shape[1:], ext.fields[key].shape)
        assert type_match(output[key].dtype, ext.fields[key].dtype)


def test_feature_stft_mag(audio, SR, HOP_LENGTH, n_fft, conv, log):

    ext = pumpp.feature.STFTMag(name='stft',
                                sr=SR, hop_length=HOP_LENGTH,
                                n_fft=n_fft,
                                conv=conv)

    output = ext.transform(**audio)

    # Check the fields
    assert set(output.keys()) == set(ext.fields.keys())

    for key in ext.fields:
        assert shape_match(output[key].shape[1:], ext.fields[key].shape)
        assert type_match(output[key].dtype, ext.fields[key].dtype)


# Mel features
def test_feature_mel_fields(SR, HOP_LENGTH, n_fft, n_mels, conv):

    ext = pumpp.feature.Mel(name='mel',
                            sr=SR, hop_length=HOP_LENGTH,
                            n_fft=n_fft, n_mels=n_mels,
                            conv=conv)

    # Check the fields
    assert set(ext.fields.keys()) == set(['mel/mag'])

    __check_shape(ext.fields, 'mel/mag', n_mels, conv)
    assert ext.fields['mel/mag'].dtype is np.float32


def test_feature_mel(audio, SR, HOP_LENGTH, n_fft, n_mels, conv, log):

    ext = pumpp.feature.Mel(name='mel',
                            sr=SR, hop_length=HOP_LENGTH,
                            n_fft=n_fft, n_mels=n_mels,
                            conv=conv)

    output = ext.transform(**audio)

    # Check the fields
    assert set(output.keys()) == set(ext.fields.keys())

    for key in ext.fields:
        assert shape_match(output[key].shape[1:], ext.fields[key].shape)
        assert type_match(output[key].dtype, ext.fields[key].dtype)


# CQT features

def test_feature_cqt_fields(SR, HOP_LENGTH, over_sample, n_octaves, conv):

    ext = pumpp.feature.CQT(name='cqt',
                            sr=SR, hop_length=HOP_LENGTH,
                            n_octaves=n_octaves,
                            over_sample=over_sample,
                            conv=conv)

    # Check the fields
    assert set(ext.fields.keys()) == set(['cqt/mag', 'cqt/phase'])

    __check_shape(ext.fields, 'cqt/mag', over_sample * n_octaves * 12, conv)
    __check_shape(ext.fields, 'cqt/phase', over_sample * n_octaves * 12, conv)
    assert ext.fields['cqt/mag'].dtype is np.float32
    assert ext.fields['cqt/phase'].dtype is np.float32


def test_feature_cqtmag_fields(SR, HOP_LENGTH, over_sample, n_octaves, conv):

    ext = pumpp.feature.CQTMag(name='cqt',
                               sr=SR, hop_length=HOP_LENGTH,
                               n_octaves=n_octaves,
                               over_sample=over_sample,
                               conv=conv)

    # Check the fields
    assert set(ext.fields.keys()) == set(['cqt/mag'])

    __check_shape(ext.fields, 'cqt/mag', over_sample * n_octaves * 12, conv)
    assert ext.fields['cqt/mag'].dtype is np.float32


def test_feature_cqtphasediff_fields(SR, HOP_LENGTH, over_sample, n_octaves,
                                     conv):

    ext = pumpp.feature.CQTPhaseDiff(name='cqt',
                                     sr=SR, hop_length=HOP_LENGTH,
                                     n_octaves=n_octaves,
                                     over_sample=over_sample,
                                     conv=conv)

    # Check the fields
    assert set(ext.fields.keys()) == set(['cqt/mag', 'cqt/dphase'])

    __check_shape(ext.fields, 'cqt/mag', over_sample * n_octaves * 12, conv)
    __check_shape(ext.fields, 'cqt/dphase', over_sample * n_octaves * 12, conv)
    assert ext.fields['cqt/mag'].dtype is np.float32
    assert ext.fields['cqt/dphase'].dtype is np.float32


def test_feature_cqt(audio, SR, HOP_LENGTH, over_sample, n_octaves, conv, log):

    ext = pumpp.feature.CQT(name='cqt',
                            sr=SR, hop_length=HOP_LENGTH,
                            n_octaves=n_octaves,
                            over_sample=over_sample,
                            log=log,
                            conv=conv)

    output = ext.transform(**audio)

    assert set(output.keys()) == set(ext.fields.keys())

    for key in ext.fields:
        assert shape_match(output[key].shape[1:], ext.fields[key].shape)
        assert type_match(output[key].dtype, ext.fields[key].dtype)


def test_feature_cqtmag(audio, SR, HOP_LENGTH, over_sample, n_octaves, conv,
                        log):

    ext = pumpp.feature.CQTMag(name='cqt',
                               sr=SR, hop_length=HOP_LENGTH,
                               n_octaves=n_octaves,
                               over_sample=over_sample,
                               log=log,
                               conv=conv)

    output = ext.transform(**audio)

    assert set(output.keys()) == set(ext.fields.keys())

    for key in ext.fields:
        assert shape_match(output[key].shape[1:], ext.fields[key].shape)
        assert type_match(output[key].dtype, ext.fields[key].dtype)


def test_feature_cqtphasediff(audio, SR, HOP_LENGTH, over_sample, n_octaves,
                              conv, log):

    ext = pumpp.feature.CQTPhaseDiff(name='cqt',
                                     sr=SR, hop_length=HOP_LENGTH,
                                     n_octaves=n_octaves,
                                     over_sample=over_sample,
                                     log=log,
                                     conv=conv)

    output = ext.transform(**audio)

    assert set(output.keys()) == set(ext.fields.keys())

    for key in ext.fields:
        assert shape_match(output[key].shape[1:], ext.fields[key].shape)
        assert type_match(output[key].dtype, ext.fields[key].dtype)


# Rhythm features
def test_feature_tempogram_fields(SR, HOP_LENGTH, WIN_LENGTH, conv):

    ext = pumpp.feature.Tempogram(name='rhythm',
                                  sr=SR, hop_length=HOP_LENGTH,
                                  win_length=WIN_LENGTH,
                                  conv=conv)

    # Check the fields
    assert set(ext.fields.keys()) == set(['rhythm/tempogram'])

    __check_shape(ext.fields, 'rhythm/tempogram', WIN_LENGTH, conv)
    assert ext.fields['rhythm/tempogram'].dtype is np.float32


def test_feature_tempogram(audio, SR, HOP_LENGTH, WIN_LENGTH, conv):

    ext = pumpp.feature.Tempogram(name='rhythm',
                                  sr=SR, hop_length=HOP_LENGTH,
                                  win_length=WIN_LENGTH,
                                  conv=conv)

    output = ext.transform(**audio)

    assert set(output.keys()) == set(ext.fields.keys())

    for key in ext.fields:
        assert shape_match(output[key].shape[1:], ext.fields[key].shape)
        assert type_match(output[key].dtype, ext.fields[key].dtype)


def test_feature_temposcale_fields(SR, HOP_LENGTH, WIN_LENGTH, N_FMT, conv):

    ext = pumpp.feature.TempoScale(name='rhythm',
                                   sr=SR, hop_length=HOP_LENGTH,
                                   win_length=WIN_LENGTH,
                                   n_fmt=N_FMT,
                                   conv=conv)

    # Check the fields
    assert set(ext.fields.keys()) == set(['rhythm/temposcale'])

    __check_shape(ext.fields, 'rhythm/temposcale', 1 + N_FMT // 2, conv)
    assert ext.fields['rhythm/temposcale'].dtype is np.float32


def test_feature_temposcale(audio, SR, HOP_LENGTH, WIN_LENGTH, N_FMT, conv):

    ext = pumpp.feature.TempoScale(name='rhythm',
                                   sr=SR, hop_length=HOP_LENGTH,
                                   win_length=WIN_LENGTH,
                                   n_fmt=N_FMT,
                                   conv=conv)

    output = ext.transform(**audio)

    assert set(output.keys()) == set(ext.fields.keys())

    for key in ext.fields:
        assert shape_match(output[key].shape[1:], ext.fields[key].shape)
        assert type_match(output[key].dtype, ext.fields[key].dtype)


# HCQT features

def test_feature_hcqt_fields(SR, HOP_LENGTH, over_sample, n_octaves,
                             hconv, harmonics):

    ext = pumpp.feature.HCQT(name='hcqt',
                             sr=SR, hop_length=HOP_LENGTH,
                             n_octaves=n_octaves,
                             over_sample=over_sample,
                             conv=hconv,
                             harmonics=harmonics)

    # Check the fields
    assert set(ext.fields.keys()) == set(['hcqt/mag', 'hcqt/phase'])

    if not harmonics:
        channels = 1
    else:
        channels = len(harmonics)

    __check_shape(ext.fields, 'hcqt/mag', over_sample * n_octaves * 12,
                  hconv, channels=channels)
    __check_shape(ext.fields, 'hcqt/phase', over_sample * n_octaves * 12,
                  hconv, channels=channels)
    assert ext.fields['hcqt/mag'].dtype is np.float32
    assert ext.fields['hcqt/phase'].dtype is np.float32


def test_feature_hcqtmag_fields(SR, HOP_LENGTH, over_sample, n_octaves,
                                hconv, harmonics):

    ext = pumpp.feature.HCQTMag(name='hcqt',
                                sr=SR, hop_length=HOP_LENGTH,
                                n_octaves=n_octaves,
                                over_sample=over_sample,
                                conv=hconv, harmonics=harmonics)

    if not harmonics:
        channels = 1
    else:
        channels = len(harmonics)

    # Check the fields
    assert set(ext.fields.keys()) == set(['hcqt/mag'])

    __check_shape(ext.fields, 'hcqt/mag', over_sample * n_octaves * 12,
                  hconv, channels=channels)
    assert ext.fields['hcqt/mag'].dtype is np.float32


def test_feature_hcqtphasediff_fields(SR, HOP_LENGTH, over_sample, n_octaves,
                                      hconv, harmonics):

    ext = pumpp.feature.HCQTPhaseDiff(name='hcqt',
                                      sr=SR, hop_length=HOP_LENGTH,
                                      n_octaves=n_octaves,
                                      over_sample=over_sample,
                                      conv=hconv, harmonics=harmonics)

    if not harmonics:
        channels = 1
    else:
        channels = len(harmonics)

    # Check the fields
    assert set(ext.fields.keys()) == set(['hcqt/mag', 'hcqt/dphase'])

    __check_shape(ext.fields, 'hcqt/mag', over_sample * n_octaves * 12,
                  hconv, channels=channels)
    __check_shape(ext.fields, 'hcqt/dphase', over_sample * n_octaves * 12,
                  hconv, channels=channels)
    assert ext.fields['hcqt/mag'].dtype is np.float32
    assert ext.fields['hcqt/dphase'].dtype is np.float32


def test_feature_hcqt(audio, SR, HOP_LENGTH, over_sample, n_octaves,
                      hconv, log, harmonics):

    ext = pumpp.feature.HCQT(name='hcqt',
                             sr=SR, hop_length=HOP_LENGTH,
                             n_octaves=n_octaves,
                             over_sample=over_sample,
                             conv=hconv,
                             log=log,
                             harmonics=harmonics)

    output = ext.transform(**audio)

    assert set(output.keys()) == set(ext.fields.keys())

    for key in ext.fields:
        assert shape_match(output[key].shape[1:], ext.fields[key].shape)
        assert type_match(output[key].dtype, ext.fields[key].dtype)


def test_feature_hcqtmag(audio, SR, HOP_LENGTH, over_sample, n_octaves,
                         hconv, log, harmonics):

    ext = pumpp.feature.HCQTMag(name='hcqt',
                                sr=SR, hop_length=HOP_LENGTH,
                                n_octaves=n_octaves,
                                over_sample=over_sample,
                                conv=hconv,
                                log=log,
                                harmonics=harmonics)

    output = ext.transform(**audio)

    assert set(output.keys()) == set(ext.fields.keys())

    for key in ext.fields:
        assert shape_match(output[key].shape[1:], ext.fields[key].shape)
        assert type_match(output[key].dtype, ext.fields[key].dtype)


def test_feature_hcqtphasediff(audio, SR, HOP_LENGTH, over_sample, n_octaves,
                               hconv, log, harmonics):

    ext = pumpp.feature.HCQTPhaseDiff(name='hcqt',
                                      sr=SR, hop_length=HOP_LENGTH,
                                      n_octaves=n_octaves,
                                      over_sample=over_sample,
                                      conv=hconv,
                                      log=log,
                                      harmonics=harmonics)

    output = ext.transform(**audio)

    assert set(output.keys()) == set(ext.fields.keys())

    for key in ext.fields:
        assert shape_match(output[key].shape[1:], ext.fields[key].shape)
        assert type_match(output[key].dtype, ext.fields[key].dtype)
