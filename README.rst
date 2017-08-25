=============
piweather|AWS
=============

.. image:: https://travis-ci.org/weinshec/piweather.svg?branch=master
    :target: https://travis-ci.org/weinshec/piweather

Automatic weather station based on Python and a RaspberryPi


Features
--------

+ **Acquire** weather data from attached sensors

  - builtin support for common RaspberryPi compatible sensors include:

    - `DS18B20 <https://datasheets.maximintegrated.com/en/ds/DS18B20.pdf>`_
      temperature sensor
    - `A100R <http://www.windspeed.co.uk/ws/index.php/option=displaypage/op=page/Itemid=67>`_
      wind speed anemometer
    - `BMP280 <https://cdn-shop.adafruit.com/datasheets/BST-BMP280-DS001-11.pdf>`_
      air pressure sensor

  - easy extensible `Sensor` interface

+ **Save** acquired data to a local or remote database

  - simply configure the database access parameters

+ **Visualize** weather data through an interactive (plotly) dashboard


.. _installation::

Installation
------------

There is no *stable* release yet, but you may work with the development version

.. code-block:: bash

    git clone https://github.com/weinshec/piweather.git
    cd piweather
    pip install -e .


.. _requirements:

Requirements
------------
Besides the python dependencies listed in `requirements.txt`, you'll need the
following hardware-related RaspberryPi packages:

.. code-block:: bash

   sudo apt-get install python3-smbus python3-rpi.gpio
