Understanding the Overflow Flag
===============================

This topic guide attempts to provide details about the overflow flag that are
not available in existing resources on the subject.

**Prerequisites**

* `ADC Operation <https://www.masswerk.at/6502/6502_instruction_set.html#ADC>`_
* `SBC Operation <https://www.masswerk.at/6502/6502_instruction_set.html#SBC>`_
* `Two's Complement <https://en.wikipedia.org/wiki/Two%27s_complement>`_


Background
----------

A value is considered "signed" if it can represent both positive and negative
numbers (has a sign +-) and "unsigned" if it can only represent positive
integer values (does not have a sign). Recall that bytes stored in memory are
just bytes: they are neither signed nor unsigned. The CPU, therefore, does not
interpret values as signed or unsigned when performing an operation, but
exposes a set of flags that help the program interpret the result as signed or
unsigned. One of these flags is the "overflow" flag (V). The overflow flag is
only applicable to signed values and is set when an addition or subtraction
operation performed on two values of the same sign results in a value of the
opposite sign.


Examples
--------

.. list-table::
   :widths: 25 25 50 25 25 25
   :header-rows: 1

   * - Accumulator Value
     - Operation Value
     - Operation
     - Unsigned Result
     - Signed Result
     - Overflow
   * - 0x7F (127)
     - 0x01 (1)
     - 127 + 1 (0x7F + 0x01)
     - 0x80 (128)
     - 0x80 (-128)
     - True
   * - 0xFE (-2)
     - 0x7F (127)
     - -2 - 127 (0xFE + 0x81)
     - 0x7F (127)
     - 0x7F (127)
     - True

**Example 1 Description:**

Overflow has occurred because both of the input values 127 and 1 have the same
sign, but the result of the operation has a different sign (-128) and is
incorrect. The diagram below shows ordered hexadecimal values and the
corresponding signed value in decimal. The signed range for an 8-bit value is
(-128, 127). Adding 1 to 127 (0x7F) causes the result to exceed the maximum
positive signed value, thereby "overflowing" into the negative range.

::

   0x00 (0)
   ...
   0x7F ( 127)  (0x7F + 0x01)
   0x80 (-128)  <-----|
   0x81 (-127)
   ...
   0xFF (-1)


**Example 2 Description:**

Example 2 is slightly more complicated as it deals with subtraction. Note that
the values for the operation seem to contradict the overflow requirement of the
values having the same sign:

::

   -2 - 127 = 127 (result should be -129)
   (-)  (+)   (+)


This is not the case, however, based on the way in which the CPU performs
subtraction. The CPU performs subtraction operations by negating the operation
value and adding it to the accumulator. The same problem can be rewritten as
follows:

::

  -2 + -127 = 127 (result should be -129)
  (-)   (-)   (+)
       or
  0xFE + 0x81


When the problem is rewritten in this way the condition holds, as the sign of
both values are the same and the result has a different sign. The result is 127
because there are 128 negative values in the signed range of an 8-bit integer.
Adding -2 to -127 (-127 + -2 = -129) exceeds the range by 1, so the result is
127. This is explained further in the example below.

::

  0x00 (0)  <---*
  0x01 (1)      |
  ...           |
  0x7F ( 127)   | * Final result. The result has exceeded the max by 1.
  0x80 (-128)   |
  0x81 (-127)   |
  ...           |
  0xFE (-2)     | * Starts here and adds 0x81 (127)
  0xFF (-1) ----* * The result "wraps around" when it reaches the maximum value
                    for the 8-bit range. Once it gets to this point there are
                    still 127 values to go (0xFF - 0x80) = 127.



Why Values of the Opposite Sign Cannot Overflow
-----------------------------------------------

An overflow can never occur when the operands are of opposite sign since the
result will never exceed this range. The rationale behind this is quite simple,
but might not be readily apparent at first glance. Recall that the range for
signed values is (-128, 127).

During addition, if the maximum of each range is added the result will be -1
(0xFF).

::

  -128 + 127 = -1


During subtraction, if the the maximum of each range is subtracted the result
will be -1 (0xFF).

::

  127 - 128 = -1

It might be tempting to think that the example above should be constructed like
the examples below:

::

  127 - -128 = -1 (should be 255)
      or
  -128 - 127 = 1 (should be -255)


But recall that the CPU will actually calculate the problem as follows:

::

   127 - -128 ->  127 + 128 = -1 (should be 255)
                  (+)   (+)   (-)
       or

  -128 -  127 -> -128 + -127 = 1 (should be -255)
                  (-)    (-)  (+)


Under these circumstances the signs are actually the same and overflow occurs.

Understanding Overflow Detection Implementation in PureNES
----------------------------------------------------------

PureNES performs two checks to determine if the overflow flag should be set.

**1. The input signs are the same:**

The sign of an 8-bit value is determined by the most significant bit (MSB) in
the value. As see below, the highest order bit is set to 1 when a value is
negative in its two's complement representation.

::

  0x01 ( 1)   = 00000001
  ...
  0x7F ( 127) = 01111111
  0x80 (-128) = 10000000 * For all negative values, the MSB is set to 1
  0x81 (-127) = 10000001
  ...
  0xFE (-2)   = 11111110
  0xFF (-1)   = 11111111


For values that have the same sign, the MSB in each value should
be the same. This can be calculated using the negation of the exclusive or
(EOR) between two values. An EOR will only be true when either of the operands
are true (one is true and the other one is false) but both are not true and
both are not false. and is calculated as follows:

::

  not ((x ^ y) & 0x80)

This is broken down below

::

  operation: x ^ y

  x:       5 -> 00000101
  y:       6 -> 00000110
  EOR      -------------
  value:   3 -> 00000011

  operation: value & 0x80

  value:    3 -> 00000011
  mask:   128 -> 10000000 * (mask refers to 0x80)
  AND     ---------------
  result:   0 -> 00000000

  Finding the EOR as shown above will only determine if the signs are NOT
  the same, so the opposite must be used to determine if the signs are the
  same.

  not 00000000 = True

  Therefore these two values have the same sign.


**2. The input and result signs differ:**

The same logic in the first condition can easily be applied to the second
condition.

::

  ((x ^ result) & 0x80) != 0


This is broken down below.

::

  operation: x ^ result

  x:        5 -> 00000101
  result:  11 -> 00001011
  EOR      ---------------
  value:   14    00001110

  operation: value & 0x80

  value:   14 -> 00001110
  mask:   128 -> 10000000 * (mask refers to 0x80)
  AND     ---------------
  value:    0    00000000

  not 0 = False

  Therefore the input value and result signs do not differ.
