from app.models.brand import Brand
from app.models.category import Category
from app.models.product import Product
from app.models.product_description import ProductDescription
from app.models.product_image import ProductImage
from app.models.product_price import ProductPrice
from app.models.product_review import ProductReview
from app.models.product_specification import ProductSpecification
from app.models.product_variant import ProductVariant
from app.models.variant_attribute import VariantAttribute
from app.models.vendor import Vendor
from app.models.vendor_product import VendorProduct

# Resolve forward references
import sqlalchemy
sqlalchemy.orm.configure_mappers()
