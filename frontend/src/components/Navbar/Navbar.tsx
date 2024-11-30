import { Flex, Heading, Image } from "@chakra-ui/react";
import { Button } from "../ui/button";
import { useNavigate } from "react-router-dom";

function Navbar() {

  const navigate = useNavigate()

  return (
    <Flex bg="green" justifyContent='space-between' direction='row'padding='0px 20px' h='80px'>
      <Flex alignItems='center'>
        <Image src="../../../public/hrm_icon.jpeg" borderRadius='10px' alt="" h="40px" />
        <Button variant="plain" size="sm" color='green.100' onClick={() => navigate('/')}>
          Home
        </Button>
        <Button variant="plain" size="sm" color='green.100' onClick={() => navigate('/facilities')}>
          Admin Facilities
        </Button>
      </Flex>
      <Flex alignItems='center'>
        <Button variant="plain" size="sm" color='green.100'>
          Log In
        </Button>
        <Button id="register-btn" color='green.100' variant="outline" size="sm">
          Sign Up Now
        </Button>
      </Flex>
    </Flex>
  );
}

export default Navbar;
