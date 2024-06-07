import Crawler from "../page/Crawler";
import ProductBasic from "../page/ProductBasic";
import ProductDeatil from "../page/ProductDeatil";
import Products from "../page/Products";
import Statistics from "../page/Statistics";


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
  },
  {
    key: "Chart",
    label: "Chart",
    path: "/chart",
    container: <Statistics />,
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
  },
  {
    key: "ProductsBasic",
    label: "ProductsBasic",
    path: "/productsbasic",
    container: <ProductBasic />,
    exact: true,
  }
];
