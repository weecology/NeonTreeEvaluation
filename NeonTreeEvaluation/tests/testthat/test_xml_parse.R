context("Check xml parsing of submission document")
test_that("xml parsing creates a dataframe",{
  xml_path<-system.file("extdata","SJER_052.xml",package="NeonTreeEvaluation")
  df<-xml_parse(xml_path)
  expect_equal(dim(df)[1],10)
  expect_equal(dim(df)[2],6)
})

