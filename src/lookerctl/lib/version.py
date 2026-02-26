# Copyright (c) Warner Bros. Discovery or its subsidiaries and affiliates.
# Licensed under the MIT License. See LICENSE file in the project root for license information.
# SPDX-License-Identifier: MIT

import os

versionTag = os.environ.get('BUILD_VERSION_TAG')
version1 = versionTag.split("-")
version = version1[0]
