from rest_framework import serializers

from logistic.models import StockProduct, Product, Stock


class ProductSerializer(serializers.ModelSerializer):
    # настройте сериализатор для продукта
    class Meta:
        model = Product
        fields = ['id', 'title', 'description']


class ProductPositionSerializer(serializers.ModelSerializer):
    # настройте сериализатор для позиции продукта на складе
    class Meta:
        model = StockProduct
        fields = ['id', 'stock', 'product', 'quantity', 'price']


class StockSerializer(serializers.ModelSerializer):
    positions = ProductPositionSerializer(many=True)

    # настройте сериализатор для склада
    class Meta:
        model = Stock
        fields = ['id', 'address', 'products']

    def create(self, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # создаем склад по его параметрам
        stock = super().create(validated_data)

        # здесь вам надо заполнить связанные таблицы
        # в нашем случае: таблицу StockProduct
        # с помощью списка positions
        stock = Stock.objects.create(**validated_data)

        # Create StockProduct instances and associate them with the stock
        for position_data in positions:
            StockProduct.objects.create(stock=stock, **position_data)

        return stock

    def update(self, instance, validated_data):
        # достаем связанные данные для других таблиц
        positions = validated_data.pop('positions')

        # обновляем склад по его параметрам
        stock = super().update(instance, validated_data)

        # здесь вам надо обновить связанные таблицы
        # в нашем случае: таблицу StockProduct
        # с помощью списка positions
        # Update the stock instance
        instance.address = validated_data.get('address', instance.address)
        instance.save()

        # Update or create StockProduct instances and associate them with the stock
        for position_data in positions:
            position_id = position_data.get('id', None)
            if position_id:
                # If an ID is provided, update the existing StockProduct instance
                position = StockProduct.objects.get(id=position_id, stock=instance)
                position.product = position_data.get('product', position.product)
                position.quantity = position_data.get('quantity', position.quantity)
                position.price = position_data.get('price', position.price)
                position.save()
            else:
                # If no ID is provided, create a new StockProduct instance
                StockProduct.objects.create(stock=instance, **position_data)

        return stock
