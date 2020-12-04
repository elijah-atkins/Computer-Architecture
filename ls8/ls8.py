#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

cpu = CPU()
cpu.trace()
cpu.load()
cpu.trace()
cpu.run()
cpu.trace()