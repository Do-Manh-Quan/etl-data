import { Outlet } from "react-router-dom";
import Header from "../component/Header";

const PublicLayout = () => {
  return (
   <div className="flex flex-col h-screen justify-between">
        <Header />
        <div className="flex-1 bg-gray-100">
          <div className="h-full">
            <Outlet />
          </div>
        </div>
   </div>
  );
};

export default PublicLayout;