from rest_framework import serializers
from rest_framework.fields import empty

from service.models import ARService, Product, ProductAnalytics, ProductCategory,ProductHealth


class ARServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ARService
        fields =  '__all__'
        


class ProductSerializer(serializers.ModelSerializer):
    products = serializers.ListField( write_only=False)
    arservice = ARServiceSerializer(many=True, read_only=True,source='arservice_set')


    class Meta:
        model = Product
        fields = [
            'id',
            'product_condition',
            'name',
            'description',
            'category',
            'product_link',
            'health',
            'health_id',
            'products',
            'arservice',
            'created_at',
            'updated_at'
        ]
        # make health_id not required
        extra_kwargs = {
            'health_id': {'required': False},
        }

    
    def create(self, validated_data):
        # try:
        print(validated_data)
        print("before pop")
        # first create arservice instances from products array
        arservices = validated_data.pop('products')
        request_data = self.context['request'].data
        print(request_data)
        print(arservices)
        print("after pop")
        

        ar_services_instances = []
        for arservice in arservices:
            print(arservice)
            # get file size
            file_size = arservice['model_file'].size/1024/1024
            # file type from file name
            file_type = arservice['model_file'].name.split('.')[-1]
            print(file_size)
            print(file_type)
            instance = ARService.objects.create(name=arservice['name'], model_file=arservice['model_file'], file_size=file_size, file_type=file_type)
            ar_services_instances.append(instance)

        print("after bulk create")
        print(ar_services_instances)
        product = Product.objects.create(
            **validated_data
        )
        # set the many to many field to ar_services_instances
        product.arservice.set(ar_services_instances)
        # if product_ar_services is there fromm context then add it to product
        if 'product_ar_services' in self.context:
            print("here")
            product.arservice.add(*self.context['product_ar_services'])



        product.save()
        print("here")
        print(product)
        print(ARServiceSerializer(product.arservice.all(), many=True).data)
        # return data
        return {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'health': product.health.name,
            'health_id': product.health.id,
            'category': product.category,
            'product_link': product.product_link,
            'products': [ARServiceSerializer(product.arservice.all(), many=True).data],
            "arservice": product.arservice.all(),
            'health': product.health,
            'created_at': product.created_at,
            'updated_at': product.updated_at

        }
        # except Exception as e:
        #     raise serializers.ValidationError("Error creating product instance the error was originated from {}".format(e))

class ProductDetailSerializer(serializers.ModelSerializer):
    # change category to give back name on read
    health = serializers.StringRelatedField(
        many=False,
        read_only=True
    )
    health_id = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=True,
        source='health'
    )
    products = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields =  [
            'id',
            'name',
            'description',
            'category',
            'product_link',
            'health',
            'health_id',
            'products',
            'created_at',
            'updated_at',
        ]

    def get_products(self, obj):
        arservices = obj.arservice.filter(
            products=obj
        )
        return ARServiceSerializer(arservices, many=True).data
    
class ProductsUpdateSerializer(serializers.ModelSerializer):
    health = serializers.StringRelatedField(
        many=False,
        read_only=True
    )
    health_id = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=True,
        source='health'
    )
    products = serializers.ListField( write_only=True)
    arservice = ARServiceSerializer(many=True, read_only=True,source='arservice_set')

    class Meta:
        model = Product
        fields = [
            'product_condition',
            'category',
            'product_link',
            'health',
            'health_id',
            'products',
            'arservice',
        ]

    def update(self, instance, validated_data):
        # try :
        print("before pop")
        print(validated_data)
        request_data = self.context['request'].data
        print(request_data)
        
        # first create arservice instances from products array
        arservices = validated_data.pop('products')
        print(arservices)
        print("after pop")
        ar_services_instances = []
        for arservice in arservices:
            print(arservice)
            # get file size
            file_size = arservice['model_file'].size/1024/1024
            # file type from file name
            file_type = arservice['model_file'].name.split('.')[-1]
            print(file_size)
            print(file_type)
            instance = ARService.objects.update_or_create(name=arservice['name'], model_file=arservice['model_file'], file_size=file_size, file_type=file_type)
            ar_services_instances.append(instance)

        # perform update on product instance if the fields are present
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.category = validated_data.get('category', instance.category)
        instance.product_link = validated_data.get('product_link', instance.product_link)
        instance.health = validated_data.get('health', instance.health)
        instance.arservice.set(ar_services_instances)
        instance.save()
        return instance
    
        # except Exception as e:
        #     raise serializers.ValidationError("Error updating product instance the error was originated from {}".format(e))
            

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields =  '__all__'

class ProductHealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductHealth
        fields =  '__all__'


    
