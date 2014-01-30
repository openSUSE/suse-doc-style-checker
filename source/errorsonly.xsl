<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="xml" indent="yes" omit-xml-declaration="yes"/>

  <xsl:template match="*">
    <xsl:element name="{local-name(.)}">
      <xsl:apply-templates/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="result">
    <xsl:if test="error">
      <xsl:element name="{local-name(.)}">
        <xsl:apply-templates/>
      </xsl:element>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
