Fetching Attribute Table Bytes During Rendering
================================================
|
| This segment provides more detail around how the attribute table address is
| inferred during rendering.
|
| **Prerequisites**
|
| `Nametables <https://www.nesdev.org/wiki/PPU_nametables>`_
| `Attribute Tables <https://www.nesdev.org/wiki/PPU_attribute_tables>`_

Inferring the Attribute Table Address
-------------------------------------

The `NES Dev Wiki <https://www.nesdev.org/wiki/PPU_scrolling>`_ provides an
example of how to construct the attribute address::

     attribute address = 0x23C0 | (v & 0x0C00) | ((v >> 4) & 0x38) | ((v >> 2) & 0x07)

     NN 1111 YYY XXX
     || |||| ||| +++-- high 3 bits of coarse X (x/4)
     || |||| +++------ high 3 bits of coarse Y (y/4)
     || ++++---------- attribute offset (960 bytes)
     ++--------------- nametable select

The implementation in PureNES is derived from this approach, but takes
advantage of bitfields to simplify accessing coarse_x and coarse_y::

    attr_address: int = (
                         0x23C0 |                                # 1
                         self._vram.reg & 0x0C00 |               # 2
                         (self._vram.flags.coarse_y // 4) * 8 |  # 3
                         self._vram.flags.coarse_x // 4
                    )

| The sections below describe each of these lines in greater detail.
|

**1. Attribute Table Offset**

Each nametable is 1024 bytes including the attribute table. An attribute table
is 64 bytes. The attribute table is, therefore, 960 bytes into the nametable
memory (1024 - 64)::

    # $23C0 = 0010001111000000
    $23C0 = $2000 + $03C0 (960 bytes)

|

**2. Nametable Offset**

Each nametable is 1024 bytes and the address needs to be offset based on the
nametable that is selected (1024 * NT select (0-3))::

    # $0C00 = 0000110000000000
    self._vram.reg & 0x0C00

|

**3. X and Y Offsets**

A nametable represents a 30x32 array of tiles, where each tile is 8x8 pixels::

                 coarse_x
              0 1 2 3 ... 31
              1
    coarse_y  2
              3
              ...
              29

An attribute table is represented as an 8x8 array of bytes, where each byte
"controls" a section of 4x4 (16) tiles in a nametable. To select the correct
byte, the values of coarse_x and coarse_y are mapped to a range(0, 7) and
incremented every fourth value. This is accomplished by using the floor
division operation::

    coarse_y  attribute_offset
    0 // 4    0
    1 // 4    0
    2 // 4    0
    3 // 4    0
    4 // 4    1
          ...
    18 // 4   4
          ...
    31 // 4   7

Finally, the x and y offsets can be calculated as follows::

    ((coarse_y // 4) * 8) + (coarse_x // 4)
