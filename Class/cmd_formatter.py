
import unittest





def format_cmd(cmd):
   print "input command = " + str(cmd) 
   count=0
   for i in range (len(str(cmd))):
      i+=count 
      if cmd [i] == '"' or  cmd [i] =='$': 
            cmd =cmd [:i] + '/' + cmd [i:]
            count+=1;
   print "output command = " +str(cmd) 
   return cmd
   
   
class Testformat_cmd(unittest.TestCase):
    def test_format_cmd(self):        
        self.assertEqual(format_cmd('"'),'/"')
        self.assertEqual(format_cmd(''),'')
        self.assertEqual(format_cmd('$$'),'/$/$')
        self.assertEqual(format_cmd('a$$'),'a/$/$')
        self.assertEqual(format_cmd('a$$b'),'a/$/$b')
        self.assertEqual(format_cmd('$$"'),'/$/$/"')
        self.assertEqual(format_cmd('$$"aa$$"'),'/$/$/"aa/$/$/"')
         
        
if __name__ == "__main__":
    unittest.main()

