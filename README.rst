Telepython
==========

What is?
--------

Telepyhton exports Python modules to XML. You send a query to Telepython, and
it returns the result of a method in XML.

What?
-----

Let us see. First, let us create a module::

    >>> import new
    >>> mymodule = new.module('mymodule', 'A test module')
    >>> def plus_three_in_list(a):
    ...     return [a+3]
    ... 
    >>> mymodule.plus_three_in_list = plus_three_in_list
    >>> mymodule.plus_three_in_list(4)
    [7]

Now, we use Telepython::

    >>> import telepython
    >>> xmlized = telepython.xml_module(mymodule)
    >>> doc = xmlized.call('plus_three_in_list', '4')
    >>> doc
    '<?xml version="1.0"?><list id="1"><int value="7" /></list>'

Note that lists have ids. All complex objects have one. They are unique *per 
XML module instance*, and are unique for each object instantiated by a
module::

    >>> def concat_a_in_list(s):
    ...     return [s+'a']
    >>> mymodule.concat_a_in_list = concat_a_in_list
    >>> mymodule.concat_a_in_list('b')
    ['ba']
    >>> xmlized = telepython.xml_module(mymodule)
    >>> xmlized.call('plus_three_in_list', '4')
    '<?xml version="1.0"?><list id="1"><int value="7" /></list>'
    >>> xmlized.call('concat_a_in_list', '"b"')
    '<?xml version="1.0"?><list id="2"><str value="ba" /></list>'
    >>> xmlized.call('plus_three_in_list', '4')
    '<?xml version="1.0"?><list id="3"><int value="7" /></list>'

Getting object by id
--------------------

If you got a complex object, you can retrieve it by its id::

    >>> xmlized.get_by_id('3')
    '<?xml version="1.0"?><list id="3"><int value="7" /></list>'

Using a native module
---------------------

Now, consider the example above::

    >>> import math
    >>> xmlized_math = telepython.xml_module(math)
    >>> doc = xmlized_math.call('cos', str(math.pi))
    >>> doc
    '<?xml version="1.0"?><float value="-1.0" />'
    >>> doc = xmlized_math.call('sin', str(math.pi/2))
    >>> doc
    '<?xml version="1.0"?><float value="1.0" />'

Dictionaries
------------

We can do it with dictionaries, too::

    >>> dictmodule = new.module('dictmodule', 'A test module')
    >>> def put_in_dict(key, value):
    ...     return {key : value}
    ... 
    >>> dictmodule.put_in_dict = put_in_dict
    >>> dictmodule.put_in_dict('a', 4)
    {'a': 4}

    >>> xmlized_dict = telepython.xml_module(dictmodule)
    >>> doc = xmlized_dict.call('put_in_dict', '"a"', '4')
    >>> doc
    '<?xml version="1.0"?><dict id="1"><key><str value="a" /></key><value><int value="4" /></value></dict>'
    >>> doc = xmlized_dict.call('put_in_dict', '"\\"a"', '4')
    >>> doc
    '<?xml version="1.0"?><dict id="2"><key><str value="&quot;a" /></key><value><int value="4" /></value></dict>'

Objects
-------

What about objects? We will try to teletransport some of them! Now, let us try
with a complex number::

    >>> complexmodule = new.module('complexmodule')
    >>> complexmodule.complex = 3+4j
    >>> xmlized_complex = telepython.xml_module(complexmodule)
    >>> xmlized_complex.get('complex')
    '<?xml version="1.0"?><complex id="1"><imag><float value="4.0" /></imag><real><float value="3.0" /></real></complex>'

Before you call it a ploy, let us do it with an user-created class::

    >>> class Person(object):
    ...     def __init__(self, name, age, friend=None):
    ...         self.name = name
    ...         self.age = age
    ...         self.friend = friend
    ... 
    >>> personmodule = new.module('personmodule')
    >>> personmodule.person1 = Person('Adam', 24)
    >>> personmodule.person2 = Person('Juliana', 25, personmodule.person1)
    >>> personmodule.person1.friend = personmodule.person2
    >>> xmlized_person = telepython.xml_module(personmodule)
    >>> xmlized_person.get('person2')
    '<?xml version="1.0"?><Person id="1"><age><int value="25" /></age><friend><Person id="2"><age><int value="24" /></age><friend><Person id="1" /></friend><name><str value="Adam" /></name></Person></friend><name><str value="Juliana" /></name></Person>'

Since we can call functions - actually, this is probably the funniest 
functionality in Telepython - we can instantiate objects as well::

    >>> personmodule.Person = Person
    >>> xmlized_person = telepython.xml_module(personmodule)
    >>> xmlized_person.call('Person', '"Pedro"', '24')
    '<?xml version="1.0"?><Person id="1"><age><int value="24" /></age><friend><None /></friend><name><str value="Pedro" /></name></Person>'

Exceptions
----------

This is a very simple example::

    >>> divmodule = new.module('divmodule')
    >>> def div(n, d):
    ...     return n/d
    ... 
    >>> div(1,2)
    0
    >>> div(1.0,2)
    0.5
    >>> divmodule.div = div

Naturally, Telepython can handle it::

    >>> xmlized_div = telepython.xml_module(divmodule)
    >>> doc = xmlized_div.call('div', '1', '2')
    >>> doc
    '<?xml version="1.0"?><int value="0" />'
    >>> doc = xmlized_div.call('div', '1.0', '2')
    >>> doc
    '<?xml version="1.0"?><float value="0.5" />'

However, problems may occur::


    >>> div(1.0,0)
    Traceback (most recent call last):
      ...
    ZeroDivisionError: float division

Can Telepython handle it? Yes::

    >>> xmlized_div.call('div', '1.0', '0')
    '<?xml version="1.0"?><raise exception="ZeroDivisionError" id="1"><message><str value="float division" /></message></raise>'

Note: this is different from getting a not raised ``Exception`` instance::

    >>> def return_zde():
    ...     return ZeroDivisionError("error!")
    >>> divmodule.return_zde = return_zde
    >>> xmlized_div = telepython.xml_module(divmodule)
    >>> xmlized_div.call('return_zde')
    '<?xml version="1.0"?><ZeroDivisionError id="1"><args><tuple id="2"><str value="error!" /></tuple></args><message><str value="error!" /></message></ZeroDivisionError>'

Variables
---------

Telepython can work with module variables::

    >>> varmodule = new.module('varmodule')
    >>> varmodule.list = ['a', 1, 0.0]
    >>> xmlized_var = telepython.xml_module(varmodule)
    >>> xmlized_var.get('list')
    '<?xml version="1.0"?><list id="1"><str value="a" /><int value="1" /><float value="0.0" /></list>'

However, you cannot call attributes::

    >>> xmlized_var.call('list', '"a"', '1', '0.0')
    '<?xml version="1.0"?><raise exception="TypeError" id="2"><message><str value="&apos;list&apos; object is not callable" /></message></raise>'

Recursion
---------

What about recursive objects? We can handle it::

    >>> varmodule.list = ['a', 1, 0.0]
    >>> varmodule.list.append(varmodule.list)
    >>> varmodule.list
    ['a', 1, 0.0, [...]]
    >>> xmlized_var = telepython.xml_module(varmodule)
    >>> xmlized_var.get('list')
    '<?xml version="1.0"?><list id="1"><str value="a" /><int value="1" /><float value="0.0" /><list id="1" /></list>'
    
Also with dicts::

    >>> varmodule.dict = {'a': 1}
    >>> varmodule.dict['b'] = varmodule.dict
    >>> varmodule.dict
    {'a': 1, 'b': {...}}
    >>> xmlized_var = telepython.xml_module(varmodule)
    >>> xmlized_var.get('dict')
    '<?xml version="1.0"?><dict id="1"><key><str value="a" /></key><value><int value="1" /></value><key><str value="b" /></key><value><dict id="1" /></value></dict>'

How far can we go? Very far, actually::

    >>> varmodule.list = ['a', 1]
    >>> varmodule.dict = {'b': 2}
    >>> varmodule.list.append(varmodule.dict)
    >>> varmodule.dict['c'] = varmodule.list
    >>> varmodule.list
    ['a', 1, {'c': [...], 'b': 2}]
    >>> varmodule.dict
    {'c': ['a', 1, {...}], 'b': 2}
    >>> xmlized_var = telepython.xml_module(varmodule)
    >>> xmlized_var.get('list')
    '<?xml version="1.0"?><list id="1"><str value="a" /><int value="1" /><dict id="2"><key><str value="b" /></key><value><int value="2" /></value><key><str value="c" /></key><value><list id="1" /></value></dict></list>'
    >>> xmlized_var.get('dict')
    '<?xml version="1.0"?><dict id="2"><key><str value="b" /></key><value><int value="2" /></value><key><str value="c" /></key><value><list id="1"><str value="a" /><int value="1" /><dict id="2" /></list></value></dict>'
    
What about None?
----------------

Could we represent ``None``? Of course we can::

    >>> nonemodule = new.module('nonemodule')
    >>> nonemodule.none = None
    >>> xmlized_none = telepython.xml_module(nonemodule)
    >>> xmlized_none.get('none')
    '<?xml version="1.0"?><None />'

Chains of attributes
--------------------

We can also get a chain of attributes::

    >>> class Chain(object):
    ...     def __init__(self, next=None, value=None):
    ...         self.next = next
    ...         self.value = value
    ...
    >>> first = Chain(value="Here I am!")
    >>> second = Chain(first)
    >>> third = Chain(second)
    >>> chainmodule = new.module('chainmodule')
    >>> chainmodule.third = third
    >>> xmlized_chain = telepython.xml_module(chainmodule)
    >>> xmlized_chain.get('third')
    '<?xml version="1.0"?><Chain id="1"><next><Chain id="2"><next><Chain id="3"><next><None /></next><value><str value="Here I am!" /></value></Chain></next><value><None /></value></Chain></next><value><None /></value></Chain>'
    >>> xmlized_chain.get('third.next')
    '<?xml version="1.0"?><Chain id="2"><next><Chain id="3"><next><None /></next><value><str value="Here I am!" /></value></Chain></next><value><None /></value></Chain>'
    >>> xmlized_chain.get('third.next.next')
    '<?xml version="1.0"?><Chain id="3"><next><None /></next><value><str value="Here I am!" /></value></Chain>'
    >>> xmlized_chain.get('third.next.next.value')
    '<?xml version="1.0"?><str value="Here I am!" />'


