import React from "react";
import { Container, Nav, Navbar } from "react-bootstrap";
import handleLogout from "../requests/Logout";

const MainNavbar = () => {
  const userIsLoggedIn = localStorage.getItem("token");
  const Logout = ({ onLogout }) => {
    return <button onClick={onLogout}>Logout</button>;
  };

  return (
    <Navbar>
      <Container>
        <Navbar.Brand href="/">Site</Navbar.Brand>
        <Navbar.Collapse>
          <Nav>
            {userIsLoggedIn ? (
              <Nav>
                <Nav.Link href="/upload/"> Upload Video</Nav.Link>
                <Nav.Link href="/video/"> Video Page</Nav.Link>
                <Nav.Link href="/recommendations/"> Recommendations</Nav.Link>
                <Nav.Link href="/view/"> View</Nav.Link>
                <Logout onLogout={handleLogout} />
              </Nav>
            ) : (
              <Nav>
                <Nav.Link href="/login/">Login</Nav.Link>
                <Nav.Link href="/verification/">Verification</Nav.Link>
                <Nav.Link href="/register/">Register</Nav.Link>
              </Nav>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default MainNavbar;
