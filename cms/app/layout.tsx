import type { Metadata } from "next";
import { Nunito_Sans, Playfair_Display } from "next/font/google";
import { config } from "@fortawesome/fontawesome-svg-core";
import "@fortawesome/fontawesome-svg-core/styles.css";
import "./globals.css";
import { LanguageProvider } from "@/contexts/LanguageContext";
import { CartProvider } from "@/contexts/CartContext";
import { ToastProvider } from "@/components/ui/Toast";

config.autoAddCss = false;

const nunitoSans = Nunito_Sans({
  variable: "--font-nunito",
  subsets: ["latin"],
  weight: ["300", "400", "600", "700"],
});

const playfairDisplay = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
  weight: ["700"],
});

export const metadata: Metadata = {
  title: "Mountain Harvest - Tinh Hoa Nông Sản & Nhu Yếu Phẩm",
  description: "Hệ thống phân phối nông sản và nhu yếu phẩm thiên nhiên hàng đầu",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi">
      <body
        className={`${nunitoSans.variable} ${playfairDisplay.variable} font-sans antialiased bg-brand-cream text-gray-800`}
      >
        <LanguageProvider>
          <CartProvider>
            <ToastProvider>{children}</ToastProvider>
          </CartProvider>
        </LanguageProvider>
      </body>
    </html>
  );
}
