Writing Operations
==================

:doc:`Operations <../operations>` are defined as Python functions. They are passed the current deploy state, the target host and any operation arguments. Operation functions read state from the host, comparing it to the arguments, and yield **commands**.

Input: reserved arguments
~~~~~~~~~~~~~~~~~~~~~~~~~

There are a number of arguments ``pyinfra`` uses that cannot be used within operations:

+ All the `global operation arguments <../deploys.html#global-arguments>`_ are reserved for controlling how operations are executed
+ The arguments ``state``, ``host``, ``frameinfo`` and ``_line_number`` are reserved for internal use within ``pyinfra``
+ The *first* argument cannot accept ``set`` objects, as these will be removed for use as the operation name (this is legacy support for 0.x and will be removed in v2)

Output: commands
~~~~~~~~~~~~~~~~

Operations are generator functions and ``yield`` three types of command:

.. code:: python

    # Shell commands, simply represented by a string OR the `StringCommand` class
    yield 'echo "Shell!"'
    yield StringCommand('echo "Shell!"')

    # File uploads represented by the `FileUploadCommand` class
    yield FileUploadCommand(filename_or_io, remote_filename)

    # File downloads represented by the `FileDownloadCommand` class
    yield FileDownloadCommand(remote_filename, filename_or_io)

    # Python functions represented by the `FunctionCommand` class
    yield FunctionCommand(function, args_list, kwargs_dict)

    # Additionally, commands can override some of the global arguments
    yield StringCommand('echo "Shell!"', sudo=True)

Example: managing files
~~~~~~~~~~~~~~~~~~~~~~~

This is a simplified version of the ``files.file`` operation, which will create/remove a
remote file based on the ``present`` kwargs:

.. code:: python

    from pyinfra.api import operation

    @operation
    def file(state, host, name, present=True):
        '''
        Manage the state of files.

        + name: name/path of the remote file
        + present: whether the file should exist
        '''

        info = host.fact.file(name)

        # Not a file?!
        if info is False:
            raise OperationError('{0} exists and is not a file'.format(name))

        # Doesn't exist & we want it
        if info is None and present:
            yield 'touch {0}'.format(name)

        # It exists and we don't want it
        elif info and not present:
            yield 'rm -f {0}'.format(name)
