import Hero from "../components/home-page-components/Hero";
import Features from "../components/home-page-components/Features";
import ProductCategories from "../components/home-page-components/ProductCategories";
import Newsletter from "../components/home-page-components/Newsletter";
import Footer from "../components/home-page-components/Footer";

export default function Home() {
  return (
    <>
      <Hero />
      <Features />
      <ProductCategories />
      <Newsletter />
      <Footer />
    </>
  );
}
