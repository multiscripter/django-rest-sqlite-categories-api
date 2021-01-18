import re

from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category
from .serializers import CategorySerializer


class CategoryView(APIView):
    def get(self, request, id=None):
        if not id:
            return Response(
                data=[{'error': 'Category id is required'}],
                status=status.HTTP_400_BAD_REQUEST
            )
        categories = []
        all = Category.objects.all()
        filtered = list(filter(lambda a: a.id == id, all))
        if filtered:
            target = filtered[0]
            name = target.name
            children = []
            children_re = r'{}\.\d$'.format(name)
            siblings = []
            s = name.split('.')
            s.pop()
            siblings_re = r'{}\.\d$'.format('.'.join(s))
            parents = []
            parent_names = []
            while len(s):
                parent_names.append('.'.join(s))
                s.pop()
            for a in all:
                if a.name in parent_names:
                    parents.append(a)
                if re.match(children_re, a.name):
                    children.append(a)
                if re.match(siblings_re, a.name) and name != a.name:
                    siblings.append(a)
            target.parents = CategorySerializer(parents, many=True).data
            target.parents = sorted(
                target.parents, key=lambda k: k['name'], reverse=True
            )
            target.children = CategorySerializer(children, many=True).data
            target.children = sorted(
                target.children, key=lambda k: k['name']
            )
            target.siblings = CategorySerializer(siblings, many=True).data
            target.siblings = sorted(
                target.siblings, key=lambda k: k['name']
            )
            categories.append(target)

        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        categories = []
        if type(request.data) is list:
            categories = request.data
        else:
            categories.append(request.data)
        errors = []
        names = []
        for a in categories:
            if not re.match(r'^Category \d+(\.\d+)*\d*$', a['name']):
                errors.append({
                    'error': 'Invalid category name: {}'.format(a['name'])
                })
            else:
                if 'children' in a and a['children']:
                    categories.extend(a['children'])
                    a.pop('children', None)
                if a['name'] in names:
                    errors.append({
                        'error': 'Name {} already exists'.format(a['name'])
                    })
                else:
                    a = Category(a['name'])

        if not errors:
            serializer = CategorySerializer(data=categories, many=True)
            if not serializer.is_valid():
                errors.append({
                    'error': 'serializer.is_valid() raised exception'
                })

        data = ''
        http_status = status.HTTP_201_CREATED
        try:
            if not errors:
                serializer.save()
            else:
                data = errors
                http_status = status.HTTP_400_BAD_REQUEST
        except BaseException as ex:
            errors.append({'error': ex.__str__()})
            data = errors
            http_status = status.HTTP_400_BAD_REQUEST
        finally:
            return Response(data=data, status=http_status)


def custom404(request, exception=None):
    return JsonResponse({
        'error': 'Not found'
    }, status = status.HTTP_404_NOT_FOUND)
