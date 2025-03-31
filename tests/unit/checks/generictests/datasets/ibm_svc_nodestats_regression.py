#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

# yapf: disable
# type: ignore



checkname = 'ibm_svc_nodestats'


info = [[u'1', u'BLUBBSVC01', u'compression_cpu_pc', u'0', u'0', u'140325134931'],
        [u'1', u'BLUBBSVC01', u'cpu_pc', u'1', u'3', u'140325134526'],
        [u'1', u'BLUBBSVC01', u'fc_mb', u'35', u'530', u'140325134526'],
        [u'1', u'BLUBBSVC01', u'fc_io', u'5985', u'11194', u'140325134751'],
        [u'1', u'BLUBBSVC01', u'sas_mb', u'0', u'0', u'140325134931'],
        [u'1', u'BLUBBSVC01', u'sas_io', u'0', u'0', u'140325134931'],
        [u'1', u'BLUBBSVC01', u'iscsi_mb', u'0', u'0', u'140325134931'],
        [u'1', u'BLUBBSVC01', u'iscsi_io', u'0', u'0', u'140325134931'],
        [u'1', u'BLUBBSVC01', u'write_cache_pc', u'0', u'0', u'140325134931'],
        [u'1', u'BLUBBSVC01', u'total_cache_pc', u'70', u'77', u'140325134716'],
        [u'1', u'BLUBBSVC01', u'vdisk_mb', u'1', u'246', u'140325134526'],
        [u'1', u'BLUBBSVC01', u'vdisk_io', u'130', u'1219', u'140325134501'],
        [u'1', u'BLUBBSVC01', u'vdisk_ms', u'0', u'4', u'140325134531'],
        [u'1', u'BLUBBSVC01', u'mdisk_mb', u'17', u'274', u'140325134526'],
        [u'1', u'BLUBBSVC01', u'mdisk_io', u'880', u'1969', u'140325134526'],
        [u'1', u'BLUBBSVC01', u'mdisk_ms', u'1', u'5', u'140325134811'],
        [u'1', u'BLUBBSVC01', u'drive_mb', u'0', u'0', u'140325134931'],
        [u'1', u'BLUBBSVC01', u'drive_io', u'0', u'0', u'140325134931'],
        [u'1', u'BLUBBSVC01', u'drive_ms', u'0', u'0', u'140325134931'],
        [u'1', u'BLUBBSVC01', u'vdisk_r_mb', u'0', u'244', u'140325134526'],
        [u'1', u'BLUBBSVC01', u'vdisk_r_io', u'19', u'1022', u'140325134501'],
        [u'1', u'BLUBBSVC01', u'vdisk_r_ms', u'2', u'8', u'140325134756'],
        [u'1', u'BLUBBSVC01', u'vdisk_w_mb', u'0', u'2', u'140325134701'],
        [u'1', u'BLUBBSVC01', u'vdisk_w_io', u'110', u'210', u'140325134901'],
        [u'1', u'BLUBBSVC01', u'vdisk_w_ms', u'0', u'0', u'140325134931'],
        [u'1', u'BLUBBSVC01', u'mdisk_r_mb', u'1', u'265', u'140325134526'],
        [u'1', u'BLUBBSVC01', u'mdisk_r_io', u'15', u'1081', u'140325134526'],
        [u'1', u'BLUBBSVC01', u'mdisk_r_ms', u'5', u'23', u'140325134616'],
        [u'1', u'BLUBBSVC01', u'mdisk_w_mb', u'16', u'132', u'140325134751'],
        [u'1', u'BLUBBSVC01', u'mdisk_w_io', u'865', u'1662', u'140325134736'],
        [u'1', u'BLUBBSVC01', u'mdisk_w_ms', u'1', u'5', u'140325134811'],
        [u'1', u'BLUBBSVC01', u'drive_r_mb', u'0', u'0', u'140325134931'],
        [u'1', u'BLUBBSVC01', u'drive_r_io', u'0', u'0', u'140325134931'],
        [u'1', u'BLUBBSVC01', u'drive_r_ms', u'0', u'0', u'140325134931'],
        [u'1', u'BLUBBSVC01', u'drive_w_mb', u'0', u'0', u'140325134931'],
        [u'1', u'BLUBBSVC01', u'drive_w_io', u'0', u'0', u'140325134931'],
        [u'1', u'BLUBBSVC01', u'drive_w_ms', u'0', u'0', u'140325134931'],
        [u'5', u'BLUBBSVC02', u'compression_cpu_pc', u'0', u'0', u'140325134930'],
        [u'5', u'BLUBBSVC02', u'cpu_pc', u'1', u'2', u'140325134905'],
        [u'5', u'BLUBBSVC02', u'fc_mb', u'141', u'293', u'140325134755'],
        [u'5', u'BLUBBSVC02', u'fc_io', u'7469', u'12230', u'140325134750'],
        [u'5', u'BLUBBSVC02', u'sas_mb', u'0', u'0', u'140325134930'],
        [u'5', u'BLUBBSVC02', u'sas_io', u'0', u'0', u'140325134930']]


discovery = {'cache': [(u'BLUBBSVC01', None)],
             'cpu_util': [(u'BLUBBSVC01', 'ibm_svc_cpu_default_levels'),
                          (u'BLUBBSVC02', 'ibm_svc_cpu_default_levels')],
             'disk_latency': [(u'Drives BLUBBSVC01', None),
                              (u'MDisks BLUBBSVC01', None),
                              (u'VDisks BLUBBSVC01', None)],
             'diskio': [(u'Drives BLUBBSVC01', None),
                        (u'MDisks BLUBBSVC01', None),
                        (u'VDisks BLUBBSVC01', None)],
             'iops': [(u'Drives BLUBBSVC01', None),
                      (u'MDisks BLUBBSVC01', None),
                      (u'VDisks BLUBBSVC01', None)]}


checks = {'cache': [(u'BLUBBSVC01',
                     {},
                     [(0,
                       'Write cache usage is 0 %, total cache usage is 70 %',
                       [('write_cache_pc', 0, None, None, 0, 100),
                        ('total_cache_pc', 70, None, None, 0, 100)])])],
          'cpu_util': [(u'BLUBBSVC01',
                        (90.0, 95.0),
                        [(0, 'Total CPU: 1.0%', [('util', 1, 90.0, 95.0, 0, 100)])]),
                       (u'BLUBBSVC02',
                        (90.0, 95.0),
                        [(0, 'Total CPU: 1.0%', [('util', 1, 90.0, 95.0, 0, 100)])])],
          'disk_latency': [(u'Drives BLUBBSVC01',
                            {},
                            [(0,
                              'Latency is 0 ms for read, 0 ms for write',
                              [('read_latency', 0, None, None, None, None),
                               ('write_latency', 0, None, None, None, None)])]),
                           (u'MDisks BLUBBSVC01',
                            {},
                            [(0,
                              'Latency is 5 ms for read, 1 ms for write',
                              [('read_latency', 5, None, None, None, None),
                               ('write_latency', 1, None, None, None, None)])]),
                           (u'VDisks BLUBBSVC01',
                            {},
                            [(0,
                              'Latency is 2 ms for read, 0 ms for write',
                              [('read_latency', 2, None, None, None, None),
                               ('write_latency', 0, None, None, None, None)])])],
          'diskio': [(u'Drives BLUBBSVC01',
                      {},
                      [(0,
                        '0.00 B/s read, 0.00 B/s write',
                        [('read', 0, None, None, None, None),
                         ('write', 0, None, None, None, None)])]),
                     (u'MDisks BLUBBSVC01',
                      {},
                      [(0,
                        '1.00 MB/s read, 16.00 MB/s write',
                        [('read', 1048576, None, None, None, None),
                         ('write', 16777216, None, None, None, None)])]),
                     (u'VDisks BLUBBSVC01',
                      {},
                      [(0,
                        '0.00 B/s read, 0.00 B/s write',
                        [('read', 0, None, None, None, None),
                         ('write', 0, None, None, None, None)])])],
          'iops': [(u'Drives BLUBBSVC01',
                    {},
                    [(0,
                      '0 IO/s read, 0 IO/s write',
                      [('read', 0, None, None, None, None),
                       ('write', 0, None, None, None, None)])]),
                   (u'MDisks BLUBBSVC01',
                    {},
                    [(0,
                      '15 IO/s read, 865 IO/s write',
                      [('read', 15, None, None, None, None),
                       ('write', 865, None, None, None, None)])]),
                   (u'VDisks BLUBBSVC01',
                    {},
                    [(0,
                      '19 IO/s read, 110 IO/s write',
                      [('read', 19, None, None, None, None),
                       ('write', 110, None, None, None, None)])])]}
