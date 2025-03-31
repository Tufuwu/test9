What is py-esp32-ulp?
---------------------

It is an assembler toolchain for the ESP32 ULP (Ultra Low-Power) Co-Processor,
written in MicroPython.

It is able to translate small, simple assembler language programs to a
loadable/executable machine code binary, at runtime, on the ESP32
microcontroller, from projects implemented in MicroPython.

This is intended as an alternative approach to assembling such programs on a
development machine using the binutils-esp32ulp toolchain from Espressif.


Status
------

The most commonly used simple stuff should work.

Expressions in assembly source code are supported and get evaluated during
assembling. Only expressions evaluating to a single integer are supported.
Constants defined with ``.set`` are supported in expressions.

We have some unit tests and also compatibility tests that compare the output
whether it is identical with binutils-esp32ulp output.

There might be some stuff missing, some bugs and other symptoms of alpha
software. Also, error and exception handling is rather rough yet.

Please be patient or contribute missing parts or fixes.

See the issue tracker for known bugs and todo items.


Links
-----

We are NOT (fully) compatible with "as", but we try to be close for the stuff
that is actually implemented:

https://sourceware.org/binutils/docs/as/index.html

Espressif docs:

https://esp-idf.readthedocs.io/en/latest/api-guides/ulp_instruction_set.html

https://www.espressif.com/sites/default/files/documentation/esp32_technical_reference_manual_en.pdf

Espressif ULP examples:

https://github.com/espressif/esp-iot-solution/tree/master/examples/ulp_examples
