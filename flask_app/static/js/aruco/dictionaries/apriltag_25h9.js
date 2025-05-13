/* Copyright (C) 2013-2016, The Regents of The University of Michigan.
All rights reserved.
This software was developed in the APRIL Robotics Lab under the
direction of Edwin Olson, ebolson@umich.edu. This software may be
available under alternative licensing terms; contact the address above.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
The views and conclusions contained in the software and documentation are those
of the authors and should not be interpreted as representing official policies,
either expressed or implied, of the Regents of The University of Michigan.
*/

//Dictionary extracted from https://github.com/AprilRobotics/apriltag-generation/blob/master/src/april/tag/Tag25h9.java

var AR = this.AR || require('../aruco').AR;
AR.DICTIONARIES['APRILTAG_25h9'] = {
  nBits: 25,
  tau: 9,
  codeList: [0x155cbf1,0x1e4d1b6,0x17b0b68,0x1eac9cd,0x12e14ce,0x3548bb,0x7757e6,0x1065dab,0x1baa2e7,0xdea688,0x81d927,0x51b241,0xdbc8ae,0x1e50e19,0x15819d2,0x16d8282,0x163e035,0x9d9b81,0x173eec4,0xae3a09,0x5f7c51,0x1a137fc,0xdc9562,0x1802e45,0x1c3542c,0x870fa4,0x914709,0x16684f0,0xc8f2a5,0x833ebb,0x59717f,0x13cd050,0xfa0ad1,0x1b763b0,0xb991ce]
};