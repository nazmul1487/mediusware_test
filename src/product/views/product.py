from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from product.models import Variant, Product, ProductVariant, ProductVariantPrice
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import redirect, render
from django.core.paginator import Paginator


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
        # return JsonResponse({"data": "New Product is created"})


class ProductsView(TemplateView):

    def get(self, request):
        all_variant_product = ProductVariantPrice.objects.all()
        product_total = len(all_variant_product)
        variants = ProductVariant.objects.all()
        option1 = []
        option2 = []
        option3 = []
        for i in variants:
            if i.variant_id == 1:
                op1 = i.variant_title
                if op1 not in option1:
                    option1.append(op1)
            if i.variant_id == 2:
                op2 = i.variant_title
                if op2 not in option2:
                    option2.append(op2)
            if i.variant_id == 3:
                op3 = i.variant_title
                if op3 not in option3:
                    option3.append(op3)

        paginator = Paginator(all_variant_product, 10)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)

        context = {
            "page_obj": page_obj,
            "product_total": product_total,
            "option1": option1,
            "option2": option2,
            "option3": option3,

        }

        return render(request, 'products/list.html', context=context)

    def post(self, request):
        pass