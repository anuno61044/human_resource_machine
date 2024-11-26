import { Flex, Heading, Image } from "@chakra-ui/react";
import { Button } from "../ui/button";

function Navbar() {
  return (
    <Flex bg="green" justifyContent='space-between' direction='row'padding='0px 20px' h='180px'>
      <Flex alignItems='center'>
        <Image src="../../../public/hrm_icon.jpeg" borderRadius='10px' alt="" h="40px" />
        <Button variant="plain" size="sm" color='green.100'>
          Products
        </Button>
      </Flex>
      <Heading size='3xl' color='green.100' alignContent='center'>Human Resource Machine</Heading>
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
