import { Button, Flex, Heading } from "@chakra-ui/react"

interface FunctionalityBoxProps {
    name:string;
}

function FunctionalityBox({name}:FunctionalityBoxProps) {


  return (
    <Button colorPalette='green' h='fit' direction='column' p='10px' borderRadius='20px' w='150px'>
        <Flex justifyContent='space-between' w='100%'>
            <Heading fontSize='20px' color='white'>{name}</Heading>
        </Flex>
    </Button>
  )
}

export default FunctionalityBox