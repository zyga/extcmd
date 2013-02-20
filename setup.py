#!/usr/bin/env python
# Copyright (c) 2010-2012 Linaro Limited
# Copyright (c) 2013 Canonical Ltd.

# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup


setup(
    name='extcmd',
    version='1.1',
    author='Zygmunt Krynicki',
    author_email='zkrynicki@gmail.com',
    url='https://github.com/zyga/extcmd',
    description='External Command - subprocess with advanced output processing',
    long_description=(
        "A convenience wrapper around subprocess.Popen that allows the caller"
        " to easily observe all stdout/stderr activity in real time."),
    packages=['extcmd'],
    test_suite='extcmd.test.test_suite',
    license="GNU LGPLv3",
    use_2to3=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
    ],
    zip_safe=True)
