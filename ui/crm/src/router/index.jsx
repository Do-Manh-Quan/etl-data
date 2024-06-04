import Crawler from "../page/Crawler";
import ProductDeatil from "../page/ProductDeatil";
import Products from "../page/Products";


export const PUBLIC_ROUTER = [
  {
    key: "crawler",
    label: "Crawler",
    path: "/",
    container: <Crawler />,
    exact: true,
  },
  {
    key: "Products",
    label: "Products",
    path: "/products",
    container: <Products />,
    exact: true,
  }
];


export const PUBLIC_ROUTER_Detail = [
  {
    key: "ProductsDetail",
    label: "ProductsDetail",
    path: "/products/:id",
    container: <ProductDeatil />,
    exact: true,
  }
];
