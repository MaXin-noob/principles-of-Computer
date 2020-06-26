# -*- coding: utf-8 -*-
#
#  Copyright (c) 2009—2010 Andrey Mikhailenko and contributors
#
#  This file is part of Tool.
#
#  Tool is free software under terms of the GNU Lesser
#  General Public License version 3 (LGPLv3) as published by the Free
#  Software Foundation. See the file README for copying conditions.
#
from context_locals import app, local
from application import Application, WebApplication #, current_app as app


__all__ = ['Application', 'WebApplication', 'app', 'local']
