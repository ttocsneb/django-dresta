# Django Decorated ReST API

A simple light weight ReST API for django that uses decorators and the
function definition to create schemas.

This allows one to use custom types as parameters, and the schema will 
convert the raw data for you. If it can't be done automatically, then you can 
create your own schemas to use.


## Creating An API method

Creating an api method is very easy. In your app, create a file called
`api.py`. In this file is where all of your api methods will be stored. From 
here, you can create a django view method that is decorated with the api 
decorator.

```py
from django.http.request import HttpRequest
from dresta.decorators import api

@api()
def my_api(request: HttpRequest, num: int, text: str):
    return {
        'data': text * num
    }
```

The above code creates an api view that will process the given GET or POST 
parameters into the parameters of `my_api`.

```
GET /api/my_app/my_api/?num=5&text=foobar
200 {
        'data': 'foobarfoobarfoobarfoobarfoobar'
    }

GET /api/my_app/my_api/?num=g&text=foobar
200 {
        'code': 400,
        'detail': 'Validation Error',
        'validation': {
            'num': ['Not a valid number.']
        }
    }
```

If you don't give a type hint to a parameter, then no processing will be done, 
and the raw value will be passed through. For any type you give: the annotator 
will try to convert the raw parameters into that object. If it doesn't do it 
how you want, you may create your own schema using the Marshmallow Schema.