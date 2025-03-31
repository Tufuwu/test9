Sparkly Session
===============

``SparklySession`` is the main entry point to sparkly's functionality.
It's derived from ``SparkSession`` to provide additional features on top of the default session.
The are two main differences between ``SparkSession`` and ``SparklySession``:

    1. ``SparklySession`` doesn't have ``builder`` attribute,
       because we prefer declarative session definition over imperative.
    2. Hive support is enabled by default.

The example below shows both imperative and declarative approaches:

.. code-block:: python

    # PySpark-style (imperative)
    from pyspark import SparkSession

    spark = SparkSession.builder\
        .appName('My App')\
        .master('spark://')\
        .config('spark.sql.shuffle.partitions', 10)\
        .getOrCreate()

    # Sparkly-style (declarative)
    from sparkly import SparklySession

    class MySession(SparklySession):
        options = {
            'spark.app.name': 'My App',
            'spark.master': 'spark://',
            'spark.sql.shuffle.partitions': 10,
        }

    spark = MySession()

    # In case you want to change default options
    spark = MySession({'spark.app.name': 'My Awesome App'})

    # In case you want to access the session singleton
    spark = MySession.get_or_create()


Installing dependencies
-----------------------

**Why**: Spark forces you to specify dependencies (spark packages or maven artifacts)
when a spark job is submitted (something like ``spark-submit --packages=...``).
We prefer a code-first approach where dependencies are actually
declared as part of the job.

**For example**: You want to read data from Cassandra.

.. code-block:: python

    from sparkly import SparklySession


    class MySession(SparklySession):
        # Define a list of spark packages or maven artifacts.
        packages = [
            'datastax:spark-cassandra-connector:2.0.0-M2-s_2.11',
        ]

    # Dependencies will be fetched during the session initialisation.
    spark = MySession()

    # Here is how you now can access a dataset in Cassandra.
    df = spark.read_ext.by_url('cassandra://<cassandra-host>/<db>/<table>?consistency=QUORUM')


Custom Maven repositories
-------------------------

**Why**: If you have a private maven repository, this is how to point spark to it when it performs a package lookup.
Order in which dependencies will be resolved is next:
 - Local cache
 - Custom maven repositories (if specified)
 - Maven Central

**For example**: Let's assume your maven repository is available on: http://my.repo.net/maven,
and there is some spark package published there, with identifier: `my.corp:spark-handy-util:0.0.1`
You can install it to a spark session like this:

.. code-block:: python

    from sparkly import SparklySession

    class MySession(SparklySession):
        repositories = ['http://my.repo.net/maven']
        packages = ['my.corp:spark-handy-util:0.0.1']

    spark = MySession()


Tuning options
--------------

**Why**: You want to customise your spark session.

**For example**:

    - ``spark.sql.shuffle.partitions`` to tune shuffling;
    - ``hive.metastore.uris`` to connect to your own HiveMetastore;
    - ``spark.hadoop.avro.mapred.ignore.inputs.without.extension`` package specific options.

.. code-block:: python

    from sparkly import SparklySession


    class MySession(SparklySession):
        options = {
            # Increase the default amount of partitions for shuffling.
            'spark.sql.shuffle.partitions': 1000,
            # Setup remote Hive Metastore.
            'hive.metastore.uris': 'thrift://<host1>:9083,thrift://<host2>:9083',
            # Ignore files without `avro` extensions.
            'spark.hadoop.avro.mapred.ignore.inputs.without.extension': 'false',
        }

    # You can also overwrite or add some options at initialisation time.
    spark = MySession({'spark.sql.shuffle.partitions': 10})


Tuning options through shell environment
----------------------------------------

**Why**: You want to customize your spark session in a way that depends on the
hardware specifications of your worker (or driver) machine(s), so you'd rather
define them close to where the actual machine specs are requested / defined.
Or you just want to test some new configuration without having to change your
code. In both cases, you can do so by using the environmental variable
``PYSPARK_SUBMIT_ARGS``. Note that any options defined this way will override
any conflicting options from your Python code.

**For example**:

    - ``spark.executor.cores`` to tune the cores used by each executor;
    - ``spark.executor.memory`` to tune the memory available to each executor.

.. code-block:: sh

    PYSPARK_SUBMIT_ARGS='--conf "spark.executor.cores=32" --conf "spark.executor.memory=160g"' \
        ./my_spark_app.py


Using UDFs
----------

**Why**: To start using Java UDF you have to import JAR file
via SQL query like ``add jar ../path/to/file`` and then call ``registerJavaFunction``.
We think it's too many actions for such simple functionality.

**For example**: You want to import UDFs from `brickhouse library <https://github.com/klout/brickhouse>`_.

.. code-block:: python

    from pyspark.sql.types import IntegerType
    from sparkly import SparklySession


    def my_own_udf(item):
        return len(item)


    class MySession(SparklySession):
        # Import local jar files.
        jars = [
            '/path/to/brickhouse.jar'
        ]
        # Define UDFs.
        udfs = {
            'collect_max': 'brickhouse.udf.collect.CollectMaxUDAF',  # Java UDF.
            'my_udf': (my_own_udf, IntegerType()),  # Python UDF.
        }

    spark = MySession()

    spark.sql('SELECT collect_max(amount) FROM my_data GROUP BY ...')
    spark.sql('SELECT my_udf(amount) FROM my_data')


Lazy access / initialization
----------------------------

**Why**: A lot of times you might need access to the sparkly session at a low-level,
deeply nested function in your code. A first approach is to declare a global sparkly
session instance that you access explicitly, but this usually makes testing painful
because of unexpected importing side effects. A second approach is to pass the session
instance explicitly as a function argument, but this makes the code ugly since you then
need to propagate that argument all the way up to every caller of that function.

Other times you might want to be able to glue together and run one after the other
different code segments, where each segment initializes its own sparkly session,
despite the sessions being identical. This situation could occur when you are doing
investigative work in a notebook.

In both cases, ``SparklySession.get_or_create`` is the answer, as it solves the
problems mentioned above while keeping your code clean and tidy.


**For example**: You want to use a read function within a transformation.

.. code-block:: python

    from sparkly import SparklySession


    class MySession(SparklySession):
        pass

    def my_awesome_transformation():
        df = read_dataset('parquet:s3://path/to/my/data')
        df2 = read_dataset('parquet:s3://path/to/my/other/data')
	# do something with df and df2...

    def read_dataset(url):
        spark = MySession.get_or_create()
        return spark.read_ext.by_url(url)


API documentation
-----------------

.. automodule:: sparkly.session
    :members:
