import { Inter } from "next/font/google";
import "./globals.css"; // Import the global stylesheet

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Home Buyer's Financial Dashboard",
  description:
    "Calculate mortgage payments and simulate future property values.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
