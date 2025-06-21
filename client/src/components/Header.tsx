import React from "react";
import { useNavigate } from "react-router-dom";
import IconButton from "./IconButton";

interface HeaderProps {
  title: string;
}

const Header: React.FC<HeaderProps> = ({ title }) => {
  console.log('Header component received title prop:', title); 
  const navigate = useNavigate();

  return (
    <header className="d-flex justify-content-between align-items-center bg-info px-4 py-3 app-header">
      <h1 className="text-white fw-bold fs-2 m-0">{title}</h1>
      <div className="d-flex gap-3">
        <IconButton.HomeButton onClick={() => navigate("/home")} />
        <IconButton.CloseButton onClick={() => navigate(-1)} />
      </div>
    </header>
  );
};

export default Header; 