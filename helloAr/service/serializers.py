from rest_framework import serializers

from service.models import ARService, Product, ProductCategory,ProductHealth


class ARServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ARService
        fields =  '__all__'
        


class ProductSerializer(serializers.ModelSerializer):
    products = serializers.ListField( write_only=True)
    arservice = ARServiceSerializer(many=True, read_only=True,source='arservice_set')

    class Meta:
        model = Product
        fields = [
            'product_condition',
            'category',
            'product_link',
            'health',
            'products',
            'arservice',
        ]


    def create(self, validated_data):
        # try:
        print(validated_data)
        print("before pop")
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
            instance = ARService.objects.create(name=arservice['name'], model_file=arservice['model_file'], file_size=file_size, file_type=file_type)
            ar_services_instances.append(instance)

        print("after bulk create")
        print(ar_services_instances)
        product = Product.objects.create(
            **validated_data
        )
        # set the many to many field to ar_services_instances
        product.arservice.set(ar_services_instances)

        product.save()
        print("here")
        print(product)
        return {
            'name': product.name,
            'description': product.description,
            'category': product.category,
            'health': product.health,
            'arservice': product.arservice,
        }
        # except Exception as e:
        #     raise serializers.ValidationError("Error creating product instance the error was originated from {}".format(e))

class ProductDetailSerializer(serializers.ModelSerializer):
    # change category to give back name on read
    category = serializers.StringRelatedField(
        many=False,
        read_only=True
    )
    health = serializers.StringRelatedField(
        many=False,
        read_only=True
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
            'products',
            'created_at',
            'updated_at',
        ]

    def get_products(self, obj):
        arservices = obj.arservice.filter(
            products=obj
        )
        return ARServiceSerializer(arservices, many=True).data

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields =  '__all__'

class ProductHealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductHealth
        fields =  '__all__'

