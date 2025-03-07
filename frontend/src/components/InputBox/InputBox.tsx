import { Box } from '@chakra-ui/react';

interface InputBoxProps {
  num: string ;
}

function InputBox({ num }: InputBoxProps) {
  return (
    <Box borderRadius="md" w='45px' overflow='hidden' textWrap='nowrap' textAlign='center' color='black' p='5px' borderBlockColor='brown' bg='white' borderWidth='4px' borderBlockStyle='solid' marginBottom='15px'>
      {num}
    </Box>
  );
}

export default InputBox;