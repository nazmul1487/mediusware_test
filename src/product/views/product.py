from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, ListView, UpdateView, FormView
from django.http import JsonResponse
from product.models import Variant, Product, ProductVariant, ProductVariantPrice, ProductImage
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import redirect, render
from django.core.paginator import Paginator
from django.db.models import Q, Count
import datetime

class CreateProductView(TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


class CreateProductAPIView(View):

    @method_decorator(csrf_exempt, name="post")
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        data = json.loads(self.request.body)
        product_data = {
            "title": data.get("title", None),
            "sku": data.get("sku", None),
            "description": data.get("description", None),
        }
        a_product = Product.objects.create(**product_data)
        # image = {}
        #
        # image = ProductImage.objects.create(data.get("product_image", None))
        product_variant_data = data.get("product_variant", None)

        variant_dict = {}
        for variant in product_variant_data:
            for tag in variant.get("tags"):
                variant_data = {
                    "product": a_product,
                    "variant_title": tag,
                    "variant": Variant.objects.filter(id=variant.get("option")).first()
                }
                a_product_variant = ProductVariant.objects.create(**variant_data)
                variant_dict[tag] = a_product_variant
            del tag
        del variant
        product_variant_prices_data = data.get("product_variant_prices", None)
        for product_variant_price in product_variant_prices_data:
            variants = product_variant_price.get("title", None).split("/")
            product_variant_price_data = {
                "product_variant_one": variant_dict[variants[0]],
                "product_variant_two": variant_dict[variants[1]],
                "product_variant_three": variant_dict[variants[2]],
                "price": product_variant_price.get("price", None),
                "stock": product_variant_price.get("stock", None),
                "product": a_product
            }
            ProductVariantPrice.objects.create(**product_variant_price_data)
        del product_variant_price
        return redirect('list.product')


class ProductsView(TemplateView):

    def get(self, request):
        query_param = request.GET
        title = query_param.get("title", None)
        variant = query_param.get("variant", None)
        price_from = query_param.get("price_from", None)
        price_to = query_param.get("price_to", None)
        date = query_param.get("date", None)
        products = Product.objects.prefetch_related("variant_price", "variant_price__product_variant_one__variant",
                                                    "variant_price__product_variant_two__variant",
                                                    "variant_price__product_variant_three__variant").all()
        if title:
            products = products.filter(title__icontains=title)
        if variant:
            products = products.filter(variants__variant_title__icontains=variant)
        if price_from and price_to:
            products = products.filter(variant_price__price__gte=float(price_from), variant_price__price__lte=float(price_to)).distinct()
        # product_total = len(products)
        if date:
            date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
            products = products.filter(created_date=date)
        variants = Variant.objects.order_by("title").values("product_variant__variant_title", "title").annotate(cnt=Count("product_variant__variant_title")).prefetch_related("product_variant")
        variants_data = {}
        for variant in variants:
            key = variant.get("title")
            value = variant.get("product_variant__variant_title")
            if variants_data.get(key):
                variants_data[key].append(value)
            else:
                variants_data[key] = [value]
        paginator = Paginator(products, 10)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)
        page_details = {
            "total_obj": paginator.count,
            "from_obj": (int(page_number)-1)*10 + 1,
            "to_obj": min(((int(page_number)-1)*10) + 10, paginator.count)
        }
        context = {
            "page_obj": page_obj,
            "current_page_obj": len(page_obj.object_list),
            "page_details": page_details,
            "variants": variants_data
        }

        return render(request, 'products/list.html', context=context)


class ProductEditView(View):

    def get(self, request, id):
        product = Product.objects.prefetch_related("variant_price").filter(id=id)
        # variants = product.prefetch_related("variants").variants.all()
        variants_stock = []
        variants_price = []
        variants_price = product.first().variant_price.all()
        variants_price_obj = []
        for vp in variants_price:
            variants_stock.append(vp.stock)
            variants_price.append(vp.price)
            # variants_price.append(vp.price)
            # variants_price[vp] = vp.stock
        # print(variants_stock)
        # print(variants_price)
        p_variants = product.first().variants.all()
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context = {
            "product": list(product.values("id", "title", "sku", "description"))[0],
            "variants_price": variants_price,
            "variants": list(variants)

        }
        return render(request, 'products/edit.html', context)

    @method_decorator(csrf_exempt, name="post")
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request, id, **kwargs):
        data = json.loads(self.request.body)
        product = Product.objects.prefetch_related("variant_price").filter(id=id).first()
        product_data = {
            "title": data.get("title", None),
            "sku": data.get("sku", None),
            "description": data.get("description", None),
        }
        product.title = product_data['title']
        product.sku = product_data['sku']
        product.description = product_data['description']
        product.save()

        return redirect('list.product')

# Edit the products, product variant price, product variant stock


# class ProductEditDjango(FormView):
#     template_name = ''
#     form_class = ''
#
#     def get(self, request, id):
#         product_data = {}
#         product = Product.objects.prefetch_related("variant_price").filter(id=id)
#         product_data['title'] = product[0].title
#         product_data['sku'] = product[0].sku
#         product_data['description'] = product[0].description
#         product_variant_data = ProductVariantPrice.objects.filter(product__id=id)
#         product_data['variant_one_stock'] = product_variant_data[0].variant_one_stock
#         product_data['variant_two_stock'] = product_variant_data[0].variant_two_stock
#         product_data['variant_three_stock'] = product_variant_data[0].variant_three_stock
#         product_data['variant_one_price'] = product_variant_data[0].variant_one_price
#         product_data['variant_two_price'] = product_variant_data[0].variant_two_price
#         product_data['variant_three_price'] = product_variant_data[0].variant_three_price
#
#         return product_data
#
#     def post(self, request, *args, **kwargs):
#         form = self.get_form()
#         if form.is_valid():
#             return self.form_valid(form)
#         return redirect('list.product')
